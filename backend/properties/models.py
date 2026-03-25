import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition
from django.core.exceptions import ValidationError
from core.models import SoftDeleteModel
from users.models import User


class Property(SoftDeleteModel):
    PROPERTY_TYPES = [
        ('agriculture', 'Agriculture Farm'),
        ('plot', 'Plot'),
        ('flat', 'Flat'),
        ('rent', 'Rent'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('changes_requested', 'Changes Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPES)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_negotiable = models.BooleanField(default=True)
    area_sqft = models.PositiveIntegerField()
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    bathrooms = models.PositiveSmallIntegerField(null=True, blank=True)

    # Location (DecimalField for dev; PostGIS PointField in prod)
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    address = models.TextField()
    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default='Belagavi')
    pincode = models.CharField(max_length=6, blank=True)

    amenities = models.JSONField(default=list, blank=True)
    status = FSMField(default='draft', choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'properties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'city']),
            models.Index(fields=['property_type', 'city']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.title} ({self.status})'

    @transition(field=status, source='draft', target='pending')
    def submit_for_review(self):
        if self.documents.count() == 0:
            raise ValidationError('Upload at least one document before submitting.')

    @transition(field=status, source='pending', target='under_review')
    def assign_advocate(self, advocate):
        from verifications.models import Verification
        Verification.objects.create(property=self, advocate=advocate)

    @transition(field=status, source='under_review', target='approved')
    def approve(self):
        self.approved_at = timezone.now()
        self.expires_at = timezone.now() + timedelta(days=90)

    @transition(field=status, source='under_review', target='changes_requested')
    def request_changes(self, remarks=''):
        pass

    @transition(field=status, source='changes_requested', target='pending')
    def resubmit(self):
        pass

    @transition(field=status, source=['under_review', 'changes_requested'], target='rejected')
    def reject(self, reason=''):
        pass

    @transition(field=status, source='approved', target='expired')
    def expire(self):
        pass


class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_images'
        ordering = ['order']


class Favorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'property']
