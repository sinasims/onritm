# shop/views.py
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import PermissionDenied
from .models import OrderItem
from storage_backends import PrivateMediaStorage

class DownloadTrackView(View):
    def get(self, request, item_id):
        try:
            order_item = OrderItem.objects.get(id=item_id)
            # اینجا باید بررسی کنی که آیا کاربر جاری، صاحب این سفارش هست یا خیر
            if request.user != order_item.order.user:
                raise PermissionDenied("شما دسترسی به این فایل ندارید.")

            # لینک موقت از استوریج خصوصی
            file_obj = order_item.track.instrumental_file
            # تولید URL موقتی با استفاده از متد url استوریج
            # (دقت کن که در متد `url` کلاس `PrivateMediaStorage`، بررسی اضافی انجام بشه)
            signed_url = file_obj.storage.url(file_obj.name)
            return JsonResponse({'download_url': signed_url})
        except OrderItem.DoesNotExist:
            return JsonResponse({'error': 'آیتم مورد نظر یافت نشد.'}, status=404)