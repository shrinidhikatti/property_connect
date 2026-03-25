from rest_framework import serializers
from .models import Conversation, Message
from users.models import User


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        # Always return masked_content — never raw content
        fields = ('id', 'masked_content', 'sender_id', 'sender_name', 'is_read', 'sent_at')

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username


class ConversationSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_id = serializers.UUIDField(source='property.id', read_only=True)
    other_party_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            'id', 'property_id', 'property_title', 'other_party_name',
            'contact_shared', 'last_message', 'unread_count',
            'created_at', 'last_message_at',
        )

    def get_other_party_name(self, obj):
        user = self.context['request'].user
        other = obj.seller if user == obj.buyer else obj.buyer
        return other.get_full_name() or other.username

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if not msg:
            return None
        return {'content': msg.masked_content, 'sent_at': msg.sent_at.isoformat()}

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()
