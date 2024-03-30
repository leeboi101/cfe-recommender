from django.contrib import admin
from django.urls import path
from .views import add_to_watchlist, remove_from_watchlist, watchlist_view


from . import views

app_name = 'anime'

urlpatterns = [
    path('', views.anime_list_view, name='anime_list_view'),
    path('infinite/', views.anime_infinite_rating_view, name='anime_infinite_view'),
    path('popular/', views.anime_popular_view, name='anime_popular_view'),
    path('<int:pk>/', views.anime_detail_view, name='anime_detail_view'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('anime/<int:anime_id>/add_to_watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('anime/<int:anime_id>/remove_from_watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
]
