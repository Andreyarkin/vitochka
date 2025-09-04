# адреса для страниц приложения viapp

from django.urls import path

from . import views

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
    # Страница добавления альбома (для администратора)
    path('add_album/', views.add_album, name='add_album'),
    # Страница добавления фотографии (для администратора)
    path('add_photo/<int:album_id>/', views.add_photo, name='add_photo'),
    # Страница скачивания фотографий
    path('download_photo/<int:photo_id>/', views.download_photo, name = 'download_photo'),
    # Страница удаления фотографии (для администратора)
    path('delete_photo/<int:photo_id>/', views.delete_photo, name = 'delete_photo'),
    # Страница для скачивания альбома целиком
    path('download_album/<int:album_id>', views.download_album, name = 'download_album'),
    # Страница удаления альбома (для администратора)
    path('delete_album/<int:album_id>/', views.delete_album, name = 'delete_album'),
    # Страница удаления нескольких выбранных фотографий в альбоме (для администратора)
    path('delete_selected_photos/<int:album_id>/', views.delete_selected_photos, name = 'delete_selected_photos'),
    # Страница выбора обложки альбома (для администратора)
    path('select_cover/<int:album_id>/<int:photo_id>/', views.select_cover, name = 'select_cover'),
    # Страница перемещения расположения фотографии (для администратора)
    path('update_photo_order/', views.update_photo_order, name = 'update_photo_order'),
    # Страница для того, чтобы делиться правом просмотра альбома
    path('albums/<int:album_id>/share/', views.share_album, name='share_album'),
]