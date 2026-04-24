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