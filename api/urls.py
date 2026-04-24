from django.urls import path
from .views import (
    SingerListView, SingerDetailView,
    TrackListView, TrackDetailView,
    MoodListView, GenreListView,
    CartView, AddToCartView, RemoveFromCartView
)

urlpatterns = [
    path('singers/', SingerListView.as_view(), name='singer-list'),
    path('singers/<slug:slug>/', SingerDetailView.as_view(), name='singer-detail'),
    path('tracks/', TrackListView.as_view(), name='track-list'),
    path('tracks/<int:id>/', TrackDetailView.as_view(), name='track-detail'),
    path('moods/', MoodListView.as_view(), name='mood-list'),
    path('genres/', GenreListView.as_view(), name='genre-list'),

    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='cart-remove'),
]