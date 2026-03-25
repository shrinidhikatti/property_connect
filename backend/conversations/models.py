import uuid
from django.db import models
from django.utils import timezone
from users.models import User
from properties.models import Property


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='conversations')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_conversations')

    # Contact sharing — unlocked when seller explicitly shares
    contact_shared = models.BooleanField(default=False)
    contact_shared_at = models.DateTimeField(null=True, blank=True)

    last_message_at = models.DateTimeField(null=True, blank=True)
    buyer_message_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        unique_together = ['property', 'buyer']
        ordering = ['-last_message_at', '-created_at']

    def __str__(self):
        return f'{self.buyer.email} ↔ {self.seller.email} re: {self.property.title}'

    def share_contact(self):
        self.contact_shared = True
        self.contact_shared_at = timezone.now()
        self.save(update_fields=['contact_shared', 'contact_shared_at'])


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')

    content = models.TextField()           # Raw — NEVER expose via API
    masked_content = models.TextField()    # Always serve this via API

    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['sent_at']
