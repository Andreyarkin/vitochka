# адреса для страниц приложения viapp

from django.urls import path

from . import views

app_name = 'viapp'
urlpatterns = [
    path('', views.index, name='index'),                    # Домашняя страница
    path('albums/', views.albums, name='albums'),           # Страница альбомов
    path('album/', views.album, name='album'),               # Страница альбома
    path('album/<int:pk>/', views.photo, name='photo'),     # Страница фотографии
]