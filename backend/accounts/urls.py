from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ChangePasswordView, LogoutView, RequestOTPView, VerifyOTPLoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', VerifyOTPLoginView.as_view(), name='verify-otp'),
]