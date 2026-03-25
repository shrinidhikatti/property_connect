from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    fields = ('sender', 'masked_content', 'is_read', 'sent_at')
    readonly_fields = ('sender', 'masked_content', 'is_read', 'sent_at')
    extra = 0
    ordering = ('sent_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'property', 'contact_shared', 'buyer_message_count', 'last_message_at', 'created_at')
    list_filter = ('contact_shared',)
    search_fields = ('buyer__email', 'seller__email', 'property__title')
    readonly_fields = ('id', 'created_at', 'updated_at', 'contact_shared_at', 'last_message_at')
    raw_id_fields = ('buyer', 'seller', 'property')
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'is_read', 'sent_at')
    list_filter = ('is_read',)
    search_fields = ('sender__email', 'masked_content')
    readonly_fields = ('id', 'sent_at', 'content', 'masked_content')
    raw_id_fields = ('conversation', 'sender')
