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


# ========== سبد خرید (برای کاربران لاگین شده و مهمان) ==========
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=40, null=True, blank=True)  # برای کاربران مهمان
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"سبد خرید {self.user.username}"
        return f"سبد خرید مهمان ({self.session_key})"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    track = models.ForeignKey('Track', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.track.price * self.quantity

    def __str__(self):
        return f"{self.track.title_fa} - تعداد: {self.quantity}"

# ========== سفارش (پس از تایید پرداخت) ==========
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('cancelled', 'لغو شده'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    session_key = models.CharField(max_length=40, null=True, blank=True)  # برای مهمان‌ها
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)  # اختیاری
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # کد رهگیری پرداخت (از زرین‌پال)
    payment_authority = models.CharField(max_length=100, blank=True, null=True)
    payment_ref_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"سفارش {self.id} - {self.first_name} {self.last_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    track = models.ForeignKey('Track', on_delete=models.CASCADE)
    price_at_purchase = models.PositiveIntegerField()  # قیمت زمان خرید (برای احتساب تغییرات قیمت بعدی)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.price_at_purchase * self.quantity

    def __str__(self):
        return f"{self.track.title_fa} - {self.order.id}"