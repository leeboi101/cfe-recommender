from django.contrib import admin
from django.urls import path


from . import views

app_name = 'anime'

urlpatterns = [
    path('', views.anime_list_view, name='anime_list_view'),
    path('infinite/', views.anime_infinite_rating_view, name='anime_infinite_view'),
    path('popular/', views.anime_popular_view, name='anime_popular_view'),
    path('<int:pk>/', views.anime_detail_view)
]