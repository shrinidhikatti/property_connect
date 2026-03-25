from django.contrib import admin
from .models import Plan, Subscription, Payment


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'price_rupees', 'listing_limit', 'validity_days', 'is_featured_included', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    ordering = ('sort_order',)

    def price_rupees(self, obj):
        return f'₹{obj.price_paise // 100}'
    price_rupees.short_description = 'Price'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'starts_at', 'expires_at', 'is_valid')
    list_filter = ('status', 'plan')
    search_fields = ('user__email',)
    readonly_fields = ('id', 'created_at')
    raw_id_fields = ('user',)

    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'amount_rupees', 'status', 'razorpay_order_id', 'created_at')
    list_filter = ('status', 'plan')
    search_fields = ('user__email', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    raw_id_fields = ('user',)

    def amount_rupees(self, obj):
        return f'₹{obj.amount_paise // 100}'
    amount_rupees.short_description = 'Amount'
