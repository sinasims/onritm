# shop/models.py
from django.db import models
from django.conf import settings
from storage_backends import PrivateMediaStorage, PublicMediaStorage

class Singer(models.Model):
    name_fa = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, allow_unicode=True)
    bio_fa = models.TextField(blank=True)
    bio_en = models.TextField(blank=True)
    image = models.ImageField(upload_to='singers/', null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name_fa

class Mood(models.Model):
    name_fa = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, allow_unicode=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name_fa']

    def __str__(self):
        return self.name_fa
    
class Genre(models.Model):
    name_fa = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, allow_unicode=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name_fa']

    def __str__(self):
        return self.name_fa
    

class Track(models.Model):

    title_fa = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE, related_name='tracks')
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True, blank=True, related_name='tracks')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='tracks')    
    price = models.PositiveIntegerField(default=50000)  # تومان
    original_file = models.FileField(upload_to='originals/', help_text="فایل اصلی آهنگ مشهور (فقط برای ادمین)")
    instrumental_file = models.FileField(upload_to='instrumentals/', help_text="فایل بی‌کلام فروشی")
    sample_file = models.FileField(upload_to='samples/', help_text="نمونه ۳۰ ثانیه‌ای")
    cover_image = models.ImageField(upload_to='covers/')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sales_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.singer.name_fa} - {self.title_fa}"

