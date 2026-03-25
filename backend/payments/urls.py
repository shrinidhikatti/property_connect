from django.urls import path
from .views import plan_list, subscription_status, create_order, verify_payment, razorpay_webhook, payment_history

urlpatterns = [
    path('plans/', plan_list, name='payment-plans'),
    path('subscription/', subscription_status, name='payment-subscription'),
    path('create-order/', create_order, name='payment-create-order'),
    path('verify/', verify_payment, name='payment-verify'),
    path('webhook/', razorpay_webhook, name='payment-webhook'),
    path('history/', payment_history, name='payment-history'),
]
