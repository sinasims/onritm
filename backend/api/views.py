from rest_framework import generics, filters
from django.shortcuts import get_object_or_404
from shop.models import Singer, Track, Mood, Genre, Cart, Order, OrderItem, CartItem
from .serializers import (
    SingerListSerializer, SingerDetailSerializer,
    TrackListSerializer, TrackDetailSerializer,
    MoodSerializer, GenreSerializer, CartSerializer, CartItemSerializer,
    CheckoutSerializer, OrderSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

class SingerListView(generics.ListAPIView):
    queryset = Singer.objects.all().order_by('order', 'name_fa')
    serializer_class = SingerListSerializer

class SingerDetailView(generics.RetrieveAPIView):
    queryset = Singer.objects.all()
    serializer_class = SingerDetailSerializer
    lookup_field = 'slug'   # استفاده از slug به جای id

class TrackListView(generics.ListAPIView):
    serializer_class = TrackListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title_fa', 'title_en', 'singer__name_fa', 'singer__name_en']
    ordering_fields = ['price', 'created_at', 'sales_count']
    ordering = ['-created_at']  # جدیدترین اول

    def get_queryset(self):
        queryset = Track.objects.filter(is_published=True)
        # فیلتر بر اساس خواننده
        singer_slug = self.request.query_params.get('singer')
        if singer_slug:
            queryset = queryset.filter(singer__slug=singer_slug)
        # فیلتر بر اساس mood
        mood_slug = self.request.query_params.get('mood')
        if mood_slug:
            queryset = queryset.filter(mood__slug=mood_slug)
        # فیلتر بر اساس genre
        genre_slug = self.request.query_params.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        return queryset

class TrackDetailView(generics.RetrieveAPIView):
    queryset = Track.objects.filter(is_published=True)
    serializer_class = TrackDetailSerializer
    lookup_field = 'id'   # یا می‌توان slug اضافه کرد

class MoodListView(generics.ListAPIView):
    queryset = Mood.objects.all().order_by('order', 'name_fa')
    serializer_class = MoodSerializer

class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all().order_by('order', 'name_fa')
    serializer_class = GenreSerializer

class CartView(APIView):
    def get_cart(self, request):
        # اگر کاربر لاگین است
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user, session_key=None)
        else:
            # برای مهمان: از session_key استفاده کن (از هدر یا کوکی)
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
        return cart

    def get(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class AddToCartView(APIView):
    def post(self, request):
        track_id = request.data.get('track_id')
        quantity = int(request.data.get('quantity', 1))
        if not track_id:
            return Response({'error': 'track_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        track = get_object_or_404(Track, id=track_id, is_published=True)
        
        # همان منطق دریافت سبد
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user, session_key=None)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, track=track)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        return Response({'message': 'added to cart'}, status=status.HTTP_200_OK)

class RemoveFromCartView(APIView):
    def post(self, request):
        item_id = request.data.get('item_id')
        if not item_id:
            return Response({'error': 'item_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # باید دسترسی را چک کنی که این آیتم متعلق به سبد فعلی کاربر است
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                return Response({'error': 'no cart'}, status=status.HTTP_400_BAD_REQUEST)
            cart = Cart.objects.filter(session_key=session_key).first()
        
        if not cart:
            return Response({'error': 'no cart'}, status=status.HTTP_400_BAD_REQUEST)
        
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        return Response({'message': 'removed'}, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    def get_cart(self, request):
        # همان منطقی که در CartView استفاده کردیم
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user, session_key=None)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
        return cart

    @transaction.atomic
    def post(self, request):
        cart = self.get_cart(request)
        if not cart.items.exists():
            return Response({'error': 'سبد خرید شما خالی است'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        total_price = cart.get_total_price()

        # ایجاد سفارش
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key if not request.user.is_authenticated else None,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email', ''),
            phone_number=data['phone_number'],
            address=data.get('address', ''),
            total_price=total_price,
            status='pending',
        )

        # انتقال آیتم‌های سبد به OrderItem
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                track=cart_item.track,
                price_at_purchase=cart_item.track.price,
                quantity=cart_item.quantity,
            )

        # خالی کردن سبد خرید
        cart.items.all().delete()

        # برگرداندن اطلاعات سفارش
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


