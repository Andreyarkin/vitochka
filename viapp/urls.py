# адреса для страниц приложения viapp

from django.urls import path

from . import views
from .views import download_photo

app_name = 'viapp'
urlpatterns = [
    # Домашняя страница
    path('', views.index, name='index'),
    # Страница альбомов
    path('albums/', views.albums, name='albums'),
    # Страница альбома
    path('albums/<int:album_id>/', views.album, name='album'),
    # Страница фотографии
    path('album/<int:photo_id>/', views.photo, name='photo'),
    # Страница добавления альбома
    path('add_album/', views.add_album, name='add_album'),
    # Страница добавления фотографии
    path('add_photo/', views.add_photo, name='add_photo'),
    # Страница скачивания фотографии
    path('download_photo/<int:photo_id>/', views.download_photo, name = 'download_photo'),
]