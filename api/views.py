from rest_framework import generics, filters
from django.shortcuts import get_object_or_404
from shop.models import Singer, Track, Mood, Genre
from .serializers import (
    SingerListSerializer, SingerDetailSerializer,
    TrackListSerializer, TrackDetailSerializer,
    MoodSerializer, GenreSerializer
)

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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from shop.models import Cart, CartItem, Track
from .serializers import CartSerializer, CartItemSerializer
from django.utils import timezone

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
