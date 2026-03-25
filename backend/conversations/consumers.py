import json
import logging
from datetime import timedelta

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import F, Q
from django.utils import timezone

from .models import Conversation, Message
from .services import ContactMaskingService

logger = logging.getLogger(__name__)

RATE_LIMIT = 10          # max messages per hour to a new seller
RATE_WINDOW = timedelta(hours=1)


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        if not await self.is_participant():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive_json(self, content):
        msg_type = content.get('type')
        if msg_type == 'chat_message':
            await self._handle_message(content)
        elif msg_type == 'typing':
            await self._handle_typing()
        elif msg_type == 'read_receipt':
            await self._mark_read()

    async def _handle_message(self, content):
        text = content.get('message', '').strip()
        if not text:
            return

        if not await self.check_rate_limit():
            await self.send_json({'type': 'error', 'message': 'Rate limit reached. Try again later.'})
            return

        message = await self.save_message(text)

        await self.channel_layer.group_send(self.room_group, {
            'type': 'chat_message',
            'message': {
                'id': str(message.id),
                'content': message.masked_content,
                'sender_id': str(self.user.id),
                'sender_name': self.user.get_full_name() or self.user.username,
                'sent_at': message.sent_at.isoformat(),
                'is_read': False,
            },
        })

        await self.notify_recipient(message)

    async def _handle_typing(self):
        await self.channel_layer.group_send(self.room_group, {
            'type': 'typing_indicator',
            'user_id': str(self.user.id),
        })

    async def _mark_read(self):
        await self.mark_messages_read()

    # ─── Channel layer event handlers ─────────────────────────────────────────

    async def chat_message(self, event):
        await self.send_json(event)

    async def typing_indicator(self, event):
        if event['user_id'] != str(self.user.id):
            await self.send_json(event)

    # ─── DB helpers ───────────────────────────────────────────────────────────

    @database_sync_to_async
    def is_participant(self):
        return Conversation.objects.filter(
            id=self.conversation_id
        ).filter(
            Q(buyer=self.user) | Q(seller=self.user)
        ).exists()

    @database_sync_to_async
    def save_message(self, text):
        from django.db import transaction
        with transaction.atomic():
            conversation = Conversation.objects.select_for_update().get(id=self.conversation_id)
            masked = ContactMaskingService.mask(text, conversation)
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=text,
                masked_content=masked,
            )
            Conversation.objects.filter(id=self.conversation_id).update(
                last_message_at=message.sent_at,
                buyer_message_count=F('buyer_message_count') + 1,
            )
        return message

    @database_sync_to_async
    def check_rate_limit(self):
        conversation = Conversation.objects.get(id=self.conversation_id)
        if conversation.contact_shared or self.user == conversation.seller:
            return True
        cutoff = timezone.now() - RATE_WINDOW
        recent = Message.objects.filter(
            conversation=conversation, sender=self.user, sent_at__gte=cutoff
        ).count()
        return recent < RATE_LIMIT

    @database_sync_to_async
    def mark_messages_read(self):
        Message.objects.filter(
            conversation_id=self.conversation_id,
            is_read=False
        ).exclude(sender=self.user).update(is_read=True)

    @database_sync_to_async
    def notify_recipient(self, message):
        from notifications.tasks import send_notification
        conversation = Conversation.objects.select_related('buyer', 'seller').get(
            id=self.conversation_id
        )
        recipient = conversation.seller if self.user == conversation.buyer else conversation.buyer
        send_notification.delay(
            str(recipient.id),
            'new_message',
            f'New message from {self.user.get_full_name() or self.user.username}',
            message.masked_content[:100],
            {'conversation_id': str(conversation.id)},
        )
