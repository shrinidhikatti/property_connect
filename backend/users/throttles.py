from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """5 attempts per minute for login / OTP send."""
    scope = 'auth'


class UploadRateThrottle(UserRateThrottle):
    """20 uploads per hour."""
    scope = 'uploads'
