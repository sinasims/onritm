# payment/urls.py
from django.urls import path
from .views import ZarinpalPaymentRequestView, ZarinpalPaymentVerifyView

urlpatterns = [
    path('request/<int:order_id>/', ZarinpalPaymentRequestView.as_view(), name='payment-request'),
    path('verify/', ZarinpalPaymentVerifyView.as_view(), name='payment-verify'),
]