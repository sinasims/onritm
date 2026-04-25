from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from shop.models import Order
from .models import Transaction

class ZarinpalPaymentRequestView(APIView):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'paid':
            return Response({'error': 'این سفارش قبلاً پرداخت شده است.'})
        
        amount = order.total_price  # ریال
        description = f'پرداخت سفارش شماره {order.id} - آنریتم'
        
        payload = {
            "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT_ID"],
            "amount": amount,
            "description": description,
            "callback_url": request.build_absolute_uri('/api/verify-payment/'),
            "metadata": {
                "mobile": order.phone_number or "",
                "email": order.email or "",
            }
        }
        
        resp = requests.post(settings.ZARINPAL_CONFIG["REQUEST_URL"], json=payload)
        data = resp.json()
        
        if data.get("data") and data["data"].get("authority"):
            authority = data["data"]["authority"]
            # ذخیره transaction
            Transaction.objects.update_or_create(
                order=order,
                defaults={'amount': amount, 'authority': authority, 'status': 'pending'}
            )
            payment_url = settings.ZARINPAL_CONFIG["STARTPAY_URL"] + authority
            return Response({'payment_url': payment_url})
        
        return Response({'error': 'خطا در ایجاد تراکنش'}, status=400)


class ZarinpalPaymentVerifyView(APIView):
    def get(self, request):
        authority = request.GET.get('Authority')
        status_param = request.GET.get('Status')
        if status_param != 'OK':
            return Response({'status': 'failed', 'error': 'پرداخت لغو شد'})
        
        try:
            transaction = Transaction.objects.get(authority=authority)
        except Transaction.DoesNotExist:
            return Response({'error': 'تراکنش یافت نشد'}, status=404)
        
        payload = {
            "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT_ID"],
            "authority": authority,
            "amount": transaction.amount,
        }
        resp = requests.post(settings.ZARINPAL_CONFIG["VERIFY_URL"], json=payload)
        data = resp.json()
        
        if data.get("data") and data["data"].get("ref_id"):
            ref_id = data["data"]["ref_id"]
            transaction.status = 'success'
            transaction.ref_id = ref_id
            transaction.save()
            
            order = transaction.order
            order.status = 'paid'
            order.payment_authority = authority
            order.payment_ref_id = ref_id
            order.save()
            
            return Response({'status': 'success', 'ref_id': ref_id})
        
        transaction.status = 'failed'
        transaction.save()
        return Response({'status': 'failed', 'error': 'پرداخت ناموفق بود'})