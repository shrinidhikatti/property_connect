import uuid
from django.db import models
from users.models import User
from properties.models import Property


class Verification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('changes_requested', 'Changes Requested'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='verifications')
    advocate = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='assigned_verifications'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    # Per-document feedback: {"ec": {"status": "rejected", "reason": "Expired"}, ...}
    document_feedback = models.JSONField(default=dict, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'verifications'
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.property.title} — {self.status}'
