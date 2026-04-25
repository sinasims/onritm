from django.contrib import admin
from .models import (
    Singer,
    Track,
    Mood,
    Genre,
    Cart,
    CartItem,
    Order,
    OrderItem,
)

# ========== اینلاین برای نمایش آهنگ‌های هر خواننده ==========
class TrackInline(admin.TabularInline):
    model = Track
    extra = 0  # تعداد ردیف خالی اضافی
    fields = ['title_fa', 'title_en', 'mood', 'genre', 'price', 'is_published']
    show_change_link = True
    # می‌توانید فیلدهای فقط خواندنی هم اضافه کنید
    readonly_fields = ['created_at', 'sales_count']

# ========== مدیریت خواننده‌ها با نمایش اینلاین آهنگ‌ها ==========
@admin.register(Singer)
class SingerAdmin(admin.ModelAdmin):
    list_display = ['name_fa', 'name_en', 'order']
    search_fields = ['name_fa', 'name_en']
    prepopulated_fields = {'slug': ('name_fa',)}
    inlines = [TrackInline]   # <-- این همان درخواست شما برای نمایش اینلاین است (اما در صفحه خواننده)

# ========== مدیریت حالت (Mood) ==========
@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ['name_fa', 'name_en', 'order']
    search_fields = ['name_fa', 'name_en']
    prepopulated_fields = {'slug': ('name_fa',)}

# ========== مدیریت ژانر (Genre) ==========
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name_fa', 'name_en', 'order']
    search_fields = ['name_fa', 'name_en']
    prepopulated_fields = {'slug': ('name_fa',)}

# ========== مدیریت اصلی آهنگ‌ها (Track) ==========
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title_fa', 'singer', 'mood', 'genre', 'price', 'is_published', 'sales_count']
    list_filter = ['singer', 'mood', 'genre', 'is_published']
    search_fields = ['title_fa', 'title_en', 'singer__name_fa']
    autocomplete_fields = ['singer', 'mood', 'genre']  # <-- جستجوی سریع و کارآمد
    fieldsets = (
        ('عنوان و خواننده', {
            'fields': ('title_fa', 'title_en', 'singer')
        }),
        ('دسته‌بندی', {
            'fields': ('mood', 'genre')
        }),
        ('فایل‌ها', {
            'fields': ('original_file', 'instrumental_file', 'sample_file', 'cover_image')
        }),
        ('قیمت و وضعیت', {
            'fields': ('price', 'is_published')
        }),
        ('آمار', {
            'fields': ('sales_count', 'created_at'),
            'classes': ('collapse',)  # بسته شدن خودکار
        }),
    )
    readonly_fields = ['sales_count', 'created_at']


# ========== اینلاین برای سبد خرید ==========
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['track', 'quantity', 'get_total_price']
    readonly_fields = ['get_total_price']
    autocomplete_fields = ['track']

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'قیمت کل آیتم'

# ========== اینلاین برای سفارش ==========
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['track', 'quantity', 'price_at_purchase', 'get_total_price']
    readonly_fields = ['price_at_purchase', 'get_total_price']
    autocomplete_fields = ['track']

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'قیمت کل آیتم'

# ========== مدیریت سبد خرید با اینلاین ==========
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at', 'updated_at', 'get_total_price']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['get_total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'جمع سبد'

# ========== مدیریت سفارش با اینلاین ==========
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    inlines = [OrderItemInline]
    readonly_fields = ['total_price', 'payment_authority', 'payment_ref_id', 'created_at']
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('user', 'session_key', 'first_name', 'last_name', 'email', 'phone_number', 'address')
        }),
        ('مبالغ و وضعیت', {
            'fields': ('total_price', 'status', 'payment_authority', 'payment_ref_id')
        }),
        ('زمان', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ========== همچنین می‌توانی خود CartItem و OrderItem را هم مستقیماً مدیریت کنی (اختیاری) ==========
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'track', 'quantity', 'get_total_price']
    autocomplete_fields = ['cart', 'track']
    search_fields = ['cart__user__username', 'track__title_fa']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'track', 'quantity', 'price_at_purchase', 'get_total_price']
    autocomplete_fields = ['order', 'track']