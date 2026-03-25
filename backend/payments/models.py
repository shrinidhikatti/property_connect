import uuid
from django.db import models
from django.utils import timezone
from users.models import User


class Plan(models.Model):
    """Seller subscription plans."""
    CODE_FREE = 'free'
    CODE_BASIC = 'basic'
    CODE_PRO = 'pro'
    CODE_BUILDER = 'builder'

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_paise = models.PositiveIntegerField(default=0, help_text='Price in paise (INR × 100)')
    listing_limit = models.IntegerField(default=1, help_text='-1 means unlimited')
    validity_days = models.PositiveIntegerField(default=30)
    is_featured_included = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'plans'
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.name} (₹{self.price_paise // 100}/mo)'

    @property
    def price_rupees(self):
        return self.price_paise / 100


class Subscription(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.plan.name} ({self.status})'

    @property
    def is_valid(self):
        return self.status == self.STATUS_ACTIVE and self.expires_at > timezone.now()

    @property
    def listing_limit(self):
        return self.plan.listing_limit


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CAPTURED = 'captured'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CAPTURED, 'Captured'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')

    # Razorpay IDs
    razorpay_order_id = models.CharField(max_length=100, unique=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default='')
    razorpay_signature = models.CharField(max_length=200, blank=True, default='')

    amount_paise = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — ₹{self.amount_paise // 100} ({self.status})'
