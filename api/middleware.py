from django.http import JsonResponse
from django.conf import settings

class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # فقط مسیرهایی که با /api/ شروع می‌شوند را چک کن
        if request.path.startswith('/api/'):
            # گرفتن هدر X-API-Key
            api_key = request.headers.get('X-API-Key')
            # مقایسه با مقدار تنظیم شده در settings
            expected_key = getattr(settings, 'API_SECRET_KEY', None)
            if not expected_key or api_key != expected_key:
                return JsonResponse({'error': 'دسترسی غیرمجاز: API Key نامعتبر'}, status=403)
        return self.get_response(request)