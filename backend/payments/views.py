import hashlib
import hmac
import json
import logging

import requests as http_requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Plan, Payment, Subscription
from .serializers import (
    PlanSerializer, SubscriptionSerializer, PaymentSerializer,
    CreateOrderSerializer, VerifyPaymentSerializer,
)

logger = logging.getLogger(__name__)


RAZORPAY_API = 'https://api.razorpay.com/v1'


def _create_razorpay_order(amount_paise, receipt, notes):
    """Create a Razorpay order via REST API."""
    resp = http_requests.post(
        f'{RAZORPAY_API}/orders',
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
        json={'amount': amount_paise, 'currency': 'INR', 'receipt': receipt, 'notes': notes},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


@api_view(['GET'])
@permission_classes([AllowAny])
def plan_list(request):
    """Return all active plans (public)."""
    plans = Plan.objects.filter(is_active=True)
    return Response(PlanSerializer(plans, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    """Return the user's current active subscription, or None."""
    sub = (
        Subscription.objects
        .filter(user=request.user, status=Subscription.STATUS_ACTIVE, expires_at__gt=timezone.now())
        .select_related('plan')
        .order_by('-expires_at')
        .first()
    )
    if sub:
        return Response(SubscriptionSerializer(sub).data)
    # Fall back to free plan details
    free = Plan.objects.filter(code=Plan.CODE_FREE).first()
    return Response({'plan': PlanSerializer(free).data if free else None, 'status': 'free'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create a Razorpay order for a given plan.
    Idempotent: returns existing pending order if not yet paid.
    """
    ser = CreateOrderSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    plan = Plan.objects.get(code=ser.validated_data['plan_code'], is_active=True)

    if not settings.RAZORPAY_KEY_ID:
        # Dev mode — simulate order creation
        fake_order_id = f'order_dev_{plan.code}_{request.user.id}'
        Payment.objects.get_or_create(
            razorpay_order_id=fake_order_id,
            defaults={
                'user': request.user,
                'plan': plan,
                'amount_paise': plan.price_paise,
                'status': Payment.STATUS_PENDING,
            },
        )
        return Response({
            'order_id': fake_order_id,
            'amount': plan.price_paise,
            'currency': 'INR',
            'key_id': 'rzp_test_dev',
            'plan': PlanSerializer(plan).data,
        })

    try:
        order = _create_razorpay_order(
            amount_paise=plan.price_paise,
            receipt=f'sub_{request.user.id}_{plan.code}',
            notes={'user_id': str(request.user.id), 'plan_code': plan.code},
        )
    except Exception as e:
        logger.error(f'Razorpay order creation failed: {e}')
        return Response({'error': True, 'message': 'Payment gateway error.'}, status=502)

    Payment.objects.get_or_create(
        razorpay_order_id=order['id'],
        defaults={
            'user': request.user,
            'plan': plan,
            'amount_paise': plan.price_paise,
            'status': Payment.STATUS_PENDING,
        },
    )

    return Response({
        'order_id': order['id'],
        'amount': plan.price_paise,
        'currency': 'INR',
        'key_id': settings.RAZORPAY_KEY_ID,
        'plan': PlanSerializer(plan).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Verify Razorpay payment signature and activate subscription.
    Atomic + idempotent: ignores already-captured payments.
    """
    ser = VerifyPaymentSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    try:
        payment = Payment.objects.select_for_update().get(
            razorpay_order_id=d['razorpay_order_id'],
            user=request.user,
        )
    except Payment.DoesNotExist:
        return Response({'error': True, 'message': 'Order not found.'}, status=404)

    if payment.status == Payment.STATUS_CAPTURED:
        return Response({'already_captured': True, 'message': 'Payment already processed.'})

    if payment.status == Payment.STATUS_FAILED:
        return Response({'error': True, 'message': 'This order has failed.'}, status=400)

    # Verify HMAC signature
    if settings.RAZORPAY_KEY_SECRET:
        expected = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{d['razorpay_order_id']}|{d['razorpay_payment_id']}".encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, d['razorpay_signature']):
            payment.status = Payment.STATUS_FAILED
            payment.save(update_fields=['status', 'updated_at'])
            return Response({'error': True, 'message': 'Invalid payment signature.'}, status=400)

    with transaction.atomic():
        now = timezone.now()
        plan = payment.plan

        # Extend existing subscription or create new
        existing_sub = (
            Subscription.objects
            .filter(user=request.user, status=Subscription.STATUS_ACTIVE, expires_at__gt=now)
            .order_by('-expires_at')
            .first()
        )

        if existing_sub and existing_sub.plan == plan:
            # Extend by validity_days from current expiry
            existing_sub.expires_at = existing_sub.expires_at + timezone.timedelta(days=plan.validity_days)
            existing_sub.save(update_fields=['expires_at'])
            sub = existing_sub
        else:
            sub = Subscription.objects.create(
                user=request.user,
                plan=plan,
                status=Subscription.STATUS_ACTIVE,
                starts_at=now,
                expires_at=now + timezone.timedelta(days=plan.validity_days),
            )

        payment.razorpay_payment_id = d['razorpay_payment_id']
        payment.razorpay_signature = d['razorpay_signature']
        payment.status = Payment.STATUS_CAPTURED
        payment.subscription = sub
        payment.save(update_fields=['razorpay_payment_id', 'razorpay_signature', 'status', 'subscription', 'updated_at'])

    from notifications.tasks import send_notification
    send_notification.delay(
        str(request.user.id),
        'system',
        'Subscription Activated!',
        f'Your {plan.name} plan is now active until {sub.expires_at.strftime("%d %b %Y")}.',
        {'subscription_id': str(sub.id)},
    )

    return Response({
        'success': True,
        'subscription': SubscriptionSerializer(sub).data,
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def razorpay_webhook(request):
    """
    Razorpay webhook endpoint.
    Handles payment.captured and payment.failed events as backup to client-side verify.
    """
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
    if webhook_secret:
        received_sig = request.headers.get('X-Razorpay-Signature', '')
        expected = hmac.new(
            webhook_secret.encode(),
            request.body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, received_sig):
            return Response({'error': 'Invalid signature'}, status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON'}, status=400)

    event = payload.get('event')
    entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
    order_id = entity.get('order_id')

    if not order_id:
        return Response({'status': 'ignored'})

    try:
        payment = Payment.objects.get(razorpay_order_id=order_id)
    except Payment.DoesNotExist:
        return Response({'status': 'not_found'})

    if event == 'payment.captured' and payment.status != Payment.STATUS_CAPTURED:
        with transaction.atomic():
            now = timezone.now()
            plan = payment.plan
            sub = Subscription.objects.create(
                user=payment.user,
                plan=plan,
                status=Subscription.STATUS_ACTIVE,
                starts_at=now,
                expires_at=now + timezone.timedelta(days=plan.validity_days),
            )
            payment.razorpay_payment_id = entity.get('id', '')
            payment.status = Payment.STATUS_CAPTURED
            payment.subscription = sub
            payment.save(update_fields=['razorpay_payment_id', 'status', 'subscription', 'updated_at'])
        logger.info(f'Webhook: captured payment {order_id}')

    elif event == 'payment.failed' and payment.status == Payment.STATUS_PENDING:
        payment.status = Payment.STATUS_FAILED
        payment.save(update_fields=['status', 'updated_at'])
        logger.info(f'Webhook: failed payment {order_id}')

    return Response({'status': 'ok'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).select_related('plan')
    return Response(PaymentSerializer(payments, many=True).data)
