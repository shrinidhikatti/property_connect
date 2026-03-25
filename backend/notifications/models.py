import uuid
from django.db import models
from users.models import User


class Notification(models.Model):
    NOTIF_TYPES = [
        ('listing_approved', 'Listing Approved'),
        ('listing_rejected', 'Listing Rejected'),
        ('changes_requested', 'Changes Requested'),
        ('new_inquiry', 'New Inquiry'),
        ('new_message', 'New Message'),
        ('contact_shared', 'Contact Shared'),
        ('verification_assigned', 'Verification Assigned'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # extra context (property_id, etc.)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.notif_type}] {self.user.email}: {self.title}'
