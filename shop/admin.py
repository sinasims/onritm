from django.contrib import admin
from .models import Singer, Mood, Genre, Track

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