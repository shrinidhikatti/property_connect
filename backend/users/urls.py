from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from .views import RegisterView, LoginView, otp_send, otp_verify, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', TokenBlacklistView.as_view(), name='auth-logout'),
    path('otp/send/', otp_send, name='otp-send'),
    path('otp/verify/', otp_verify, name='otp-verify'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
]
