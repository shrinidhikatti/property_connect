import random
import logging
from django.core.cache import cache
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    OTPSendSerializer, OTPVerifySerializer,
    CustomTokenObtainPairSerializer,
)
from .throttles import AuthRateThrottle

logger = logging.getLogger(__name__)

OTP_EXPIRY = 600       # 10 minutes
OTP_MAX_RESENDS = 3    # per hour


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = []


@api_view(['POST'])
@permission_classes([AllowAny])
def otp_send(request):
    """Generate OTP and store in Redis; in production SMS via MSG91/Twilio."""
    serializer = OTPSendSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone = serializer.validated_data['phone']

    # Rate-limit resends
    resend_key = f'otp_resend_count:{phone}'
    resend_count = cache.get(resend_key, 0)
    if resend_count >= OTP_MAX_RESENDS:
        return Response(
            {'error': True, 'message': 'Too many OTP requests. Try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    otp = f'{random.randint(100000, 999999)}'
    cache.set(f'otp:{phone}', otp, timeout=OTP_EXPIRY)
    cache.set(resend_key, resend_count + 1, timeout=3600)

    # TODO: Send via MSG91 / Twilio in production
    # In dev, OTP is logged so you can test without an SMS provider
    logger.info(f'[DEV] OTP for {phone}: {otp}')

    return Response({'message': 'OTP sent successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def otp_verify(request):
    serializer = OTPVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone = serializer.validated_data['phone']
    otp = serializer.validated_data['otp']

    stored_otp = cache.get(f'otp:{phone}')
    if not stored_otp or stored_otp != otp:
        return Response(
            {'error': True, 'message': 'Invalid or expired OTP.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    User.objects.filter(phone=phone).update(is_phone_verified=True)
    cache.delete(f'otp:{phone}')

    return Response({'message': 'Phone verified successfully.'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
