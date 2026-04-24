# storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class PrivateMediaStorage(S3Boto3Storage):
    """
    این کلاس، استوریج مخصوص فایل‌های خصوصی مثل MP3 بی‌کلام است.
    فایل‌هایی که از این مسیر ذخیره می‌شن، مستقیماً در دسترس نیستن.
    """
    location = 'private'  # فایل‌های خصوصی در پوشه 'private' باکت ذخیره می‌شن
    default_acl = 'private'  # دسترسی پیش‌فرض روی خصوصی تنظیم میشه
    file_overwrite = False    # از بازنویسی فایل‌ها جلوگیری میکنه
    custom_domain = False     # از دامنه اختصاصی آرون استفاده نمیشه

class PublicMediaStorage(S3Boto3Storage):
    """
    این کلاس، استوریج مخصوص فایل‌های عمومی مثل کاور و تصاویر است.
    این فایل‌ها به راحتی قابل مشاهده و ذخیره هستند.
    """
    location = 'public'    # فایل‌های عمومی در پوشه 'public' باکت ذخیره می‌شن
    default_acl = 'public-read'  # دسترسی عمومی برای خوندن (خواندن)
    file_overwrite = False
    custom_domain = False