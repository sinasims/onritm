from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.utils import timezone

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username
    

class OTPCode(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at

    @classmethod
    def generate_code(cls, phone_number):
        # حذف کدهای قبلی منقضی شده یا معتبر
        cls.objects.filter(phone_number=phone_number).delete()
        code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timezone.timedelta(minutes=2)  # 2 دقیقه اعتبار
        return cls.objects.create(phone_number=phone_number, code=code, expires_at=expires_at)


