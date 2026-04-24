from rest_framework import serializers
from shop.models import Singer, Track, Mood, Genre

class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ['id', 'name_fa', 'name_en', 'slug']
        
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name_fa', 'name_en', 'slug']

class SingerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Singer
        fields = ['id', 'name_fa', 'name_en', 'slug', 'image', 'order']

class SingerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Singer
        fields = ['id', 'name_fa', 'name_en', 'slug', 'bio_fa', 'bio_en', 'image']

class TrackListSerializer(serializers.ModelSerializer):
    singer_name = serializers.CharField(source='singer.name_fa')
    cover_url = serializers.SerializerMethodField()
    sample_url = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = ['id', 'title_fa', 'title_en', 'singer', 'singer_name', 'mood', 'genre', 'price', 'cover_url', 'sample_url', 'slug']

    def get_cover_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url  # چون عمومی است
        return None

    def get_sample_url(self, obj):
        if obj.sample_file:
            return obj.sample_file.url
        return None
    
class TrackDetailSerializer(serializers.ModelSerializer):
    singer = SingerDetailSerializer()
    mood = MoodSerializer()
    genre = GenreSerializer()

    class Meta:
        model = Track
        # fields = ['id', 'title_fa', 'title_en', 'singer', 'mood', 'genre', 'price', 'cover_image', 'sample_file', 'instrumental_file', 'original_file', 'created_at']
        # remove instrumental_file برای مخفی کردن آدرس فایل
        fields = ['id', 'title_fa', 'title_en', 'singer', 'mood', 'genre', 'price', 'cover_image', 'sample_file', 'original_file', 'created_at']
        

from shop.models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    track_title = serializers.CharField(source='track.title_fa', read_only=True)
    track_price = serializers.IntegerField(source='track.price', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'track', 'track_title', 'quantity', 'track_price', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        return obj.get_total_price()
    
# api/serializers.py
class CheckoutSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=15)
    address = serializers.CharField(required=False, allow_blank=True)

# api/serializers.py (بخش اضافه شده)
from shop.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    track_title = serializers.CharField(source='track.title_fa', read_only=True)
    track_cover = serializers.ImageField(source='track.cover_image', read_only=True)
    total_price_item = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'track', 'track_title', 'track_cover', 'quantity', 'price_at_purchase', 'total_price_item']

    def get_total_price_item(self, obj):
        return obj.get_total_price()

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'total_price', 'total_price_display', 'status', 'created_at', 'items']

    def get_total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"


