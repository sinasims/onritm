# shop/views.py
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import PermissionDenied
from .models import OrderItem
from storage_backends import PrivateMediaStorage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# api/views.py

class DownloadTrackView(APIView):
    def get(self, request, order_item_id):
        try:
            order_item = OrderItem.objects.select_related('order', 'track').get(id=order_item_id)
        except OrderItem.DoesNotExist:
            return Response({'error': 'آیتم مورد نظر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        order = order_item.order
        # بررسی دسترسی کاربر
        if request.user.is_authenticated:
            if order.user != request.user:
                raise PermissionDenied("شما دسترسی به این فایل ندارید.")
        else:
            # کاربر مهمان: session_key باید با سفارش مطابقت داشته باشد
            session_key = request.session.session_key
            if not session_key or order.session_key != session_key:
                raise PermissionDenied("شما دسترسی به این فایل ندارید.")

        if order.status != 'paid':
            return Response({'error': 'این سفارش هنوز پرداخت نشده است'}, status=status.HTTP_402_PAYMENT_REQUIRED)

        # تولید لینک موقت برای فایل بی‌کلام
        file_obj = order_item.track.instrumental_file
        # اطمینان از اینکه استوریج از نوع PrivateMediaStorage است
        if not isinstance(file_obj.storage, PrivateMediaStorage):
            return Response({'error': 'تنظیمات ذخیره‌سازی فایل صحیح نیست'}, status=500)

        signed_url = file_obj.storage.url(file_obj.name)  # این متد باید لینک موقت تولید کند
        return Response({'download_url': signed_url}, status=status.HTTP_200_OK)

