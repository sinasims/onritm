from django.urls import path
from .views import (
    SingerListView, SingerDetailView,
    TrackListView, TrackDetailView,
    MoodListView, GenreListView
)

urlpatterns = [
    path('singers/', SingerListView.as_view(), name='singer-list'),
    path('singers/<slug:slug>/', SingerDetailView.as_view(), name='singer-detail'),
    path('tracks/', TrackListView.as_view(), name='track-list'),
    path('tracks/<int:id>/', TrackDetailView.as_view(), name='track-detail'),
    path('moods/', MoodListView.as_view(), name='mood-list'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
]