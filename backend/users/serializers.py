import re
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # No username field — we auto-set it from email
        fields = ('email', 'phone', 'password', 'password2', 'role',
                  'first_name', 'last_name')

    def validate_role(self, value):
        if value == 'advocate':
            raise serializers.ValidationError(
                'Advocate accounts are created by administrators only.'
            )
        return value

    def validate_phone(self, value):
        if value and not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError('Enter a valid 10-digit Indian mobile number.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        email = validated_data.get('email', '')
        phone = validated_data.get('phone', '')

        # Use email as username; fall back to phone if no email provided
        username = email or phone
        # Ensure uniqueness by appending suffix if collision (edge case)
        base = username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f'{base}_{suffix}'
            suffix += 1

        user = User(username=username, **validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'phone',
                  'role', 'is_phone_verified', 'whatsapp_opt_in', 'created_at')
        read_only_fields = ('id', 'email', 'username', 'role', 'is_phone_verified', 'created_at')


class OTPSendSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError('Enter a valid 10-digit Indian mobile number.')
        return value


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6, min_length=6)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Allow login with email OR mobile number.
    Translates either to the stored username before JWT validation.
    """

    def validate(self, attrs):
        login_input = attrs.get('username', '').strip()

        # If it looks like a phone number, find the user by phone
        if re.match(r'^[6-9]\d{9}$', login_input):
            try:
                user = User.objects.get(phone=login_input)
                attrs['username'] = user.username
            except User.DoesNotExist:
                raise AuthenticationFailed('No account found with this mobile number.')

        # If it looks like an email, find by email → get username
        elif '@' in login_input:
            try:
                user = User.objects.get(email=login_input)
                attrs['username'] = user.username
            except User.DoesNotExist:
                raise AuthenticationFailed('No account found with this email.')

        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token
