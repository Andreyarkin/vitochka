# адреса для страниц приложения viapp

from django.urls import path

from . import views

app_name = 'viapp'
urlpatterns = [
    path('', views.index, name='index'),                            # Домашняя страница
    path('albums/', views.albums, name='albums'),                   # Страница альбомов
    path('albums/<int:album_id>/', views.album, name='album'),      # Страница альбома
    path('album/<int:photo_id>/', views.photo, name='photo'),       # Страница фотографии
    path('add_album/', views.add_album, name='add_album'),          # Страница добавления альбома
    path('add_photo/', views.add_photo, name='add_photo'),          # Страница добавления фотографии
]