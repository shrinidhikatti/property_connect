from rest_framework import serializers
from .models import Plan, Subscription, Payment


class PlanSerializer(serializers.ModelSerializer):
    price_rupees = serializers.FloatField(read_only=True)

    class Meta:
        model = Plan
        fields = ('id', 'code', 'name', 'description', 'price_paise', 'price_rupees',
                  'listing_limit', 'validity_days', 'is_featured_included', 'sort_order')


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    listing_limit = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'plan', 'status', 'starts_at', 'expires_at', 'is_valid', 'listing_limit', 'created_at')


class PaymentSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'plan', 'razorpay_order_id', 'amount_paise', 'status', 'created_at')


class CreateOrderSerializer(serializers.Serializer):
    plan_code = serializers.CharField()

    def validate_plan_code(self, value):
        from .models import Plan
        try:
            plan = Plan.objects.get(code=value, is_active=True)
        except Plan.DoesNotExist:
            raise serializers.ValidationError('Invalid or inactive plan.')
        if plan.price_paise == 0:
            raise serializers.ValidationError('Free plan does not require payment.')
        return value


class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
