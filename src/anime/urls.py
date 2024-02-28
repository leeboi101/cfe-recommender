from django.contrib import admin
from django.urls import path


from . import views
urlpatterns = [
    path('', views.anime_list_view),
    path('<int:id>/', views.anime_detail_view),
]