# storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class PrivateMediaStorage(S3Boto3Storage):
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False

    def url(self, name, expire=3600):
        # برای فایل‌های خصوصی، لینک موقت با زمان انقضا بساز
        key = self._get_key(name)
        return self.connection.meta.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket.name, 'Key': key},
            ExpiresIn=expire,
        )

class PublicMediaStorage(S3Boto3Storage):
    """
    این کلاس، استوریج مخصوص فایل‌های عمومی مثل کاور و تصاویر است.
    این فایل‌ها به راحتی قابل مشاهده و ذخیره هستند.
    """
    location = 'public'    # فایل‌های عمومی در پوشه 'public' باکت ذخیره می‌شن
    default_acl = 'public-read'  # دسترسی عمومی برای خوندن (خواندن)
    file_overwrite = False
    custom_domain = False