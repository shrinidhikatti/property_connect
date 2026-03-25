from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from properties.models import Property
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('property', 'buyer', 'seller').prefetch_related('messages')

    def list(self, request):
        qs = self.get_queryset().order_by('-last_message_at', '-created_at')
        return Response(ConversationSerializer(qs, many=True, context={'request': request}).data)

    def retrieve(self, request, pk=None):
        conv = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(ConversationSerializer(conv, context={'request': request}).data)

    @action(detail=False, methods=['post'])
    def start(self, request):
        """Buyer starts a conversation on a property."""
        property_id = request.data.get('property_id')
        prop = get_object_or_404(Property, pk=property_id, status='approved')

        if prop.owner == request.user:
            return Response({'error': True, 'message': 'Cannot enquire on your own listing.'}, status=400)

        conv, created = Conversation.objects.get_or_create(
            property=prop, buyer=request.user,
            defaults={'seller': prop.owner},
        )

        if created:
            from notifications.tasks import send_notification
            send_notification.delay(
                str(prop.owner.id),
                'new_inquiry',
                f'New enquiry on {prop.title}',
                f'{request.user.get_full_name() or request.user.username} is interested in your property.',
                {'conversation_id': str(conv.id), 'property_id': str(prop.id)},
            )

        return Response(
            ConversationSerializer(conv, context={'request': request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conv = get_object_or_404(self.get_queryset(), pk=pk)
        msgs = conv.messages.order_by('sent_at')
        # Mark all incoming messages as read
        msgs.exclude(sender=request.user).update(is_read=True)
        return Response(MessageSerializer(msgs, many=True).data)

    @action(detail=True, methods=['post'])
    def share_contact(self, request, pk=None):
        """Seller shares their contact details with the buyer."""
        conv = get_object_or_404(self.get_queryset(), pk=pk)
        if request.user != conv.seller:
            return Response({'error': True, 'message': 'Only the seller can share contact.'}, status=403)
        conv.share_contact()
        from notifications.tasks import send_notification
        send_notification.delay(
            str(conv.buyer_id),
            'contact_shared',
            'Contact details unlocked!',
            f"{conv.seller.get_full_name() or conv.seller.username} shared their contact for '{conv.property.title}'.",
            {'conversation_id': str(conv.id)},
        )
        return Response({'contact_shared': True})
