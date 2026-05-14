from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Album, Photo
from django.http import FileResponse

import zipfile
import os

from io import BytesIO

def view_albums(user):
    """
    Возвращает queryset альбомов, доступных пользователю
    """
    # Неавторизованный пользователь — ничего не видит
    if not user.is_authenticated:
        return Album.objects.none()

    # Суперпользователь — видит всё
    if user.is_superuser:
        return Album.objects.all().order_by('created_at')

    # Обычный пользователь — свои + расшаренные
    return Album.objects.filter(
        Q(owner=user) | Q(shared_with=user)
    ).select_related("owner").distinct().order_by('created_at')

def view_and_download(user, album):
    return (
        user.is_superuser or
        album.owner == user or
        album.shared_with.filter(id=user.id).exists()
    )

def can_create_album(user):
    return (
        user.is_superuser or
        user.can_create_album
    )

def edit_content (user, album):
    return (
        user.is_superuser or
        album.owner == user
    )

# Функция скачивания альбома
def download_album_zip(album):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for photo in album.photos.all():
            photo_path = photo.image.path
            if os.path.exists(photo_path):
                zip_file.write(photo_path, os.path.basename(photo_path))
    zip_buffer.seek(0)
    return zip_buffer

# Функция скачивания фото
def download_photofile(photo):
    
    
    
    return FileResponse(photo.image.open(), as_attachment=True)

# функция удаления фотографий
def delete_several_photos(user, photo_ids, album):
    
    if not edit_content(user, album):
        raise PermissionDenied("У вас нет прав на удаление фотографий")
    
    queryset = Photo.objects.filter(id__in=photo_ids, album=album)
    
    deleted, _ = queryset.delete()
    return deleted
    
def share_album_service(user, album, users):
    if not edit_content(user, album):
        raise PermissionDenied("Нет прав делиться альбомом")

    album.shared_with.set(users)
    
def set_album_cover(user, album, photo):
    if not edit_content(user, album):
        raise PermissionDenied()

    if photo.album != album:
        raise PermissionDenied("Фото не из этого альбома")

    album.cover = photo
    album.save()
    
def reorder_photos(user, album, order_data):
    if not edit_content(user, album):
        raise PermissionDenied()

    photo_ids = [item["id"] for item in order_data]

    photos = Photo.objects.filter(
        id__in=photo_ids,
        album=album
    )

    if photos.count() != len(photo_ids):
        raise PermissionDenied("Некоторые фото не найдены")

    photos_dict = {
        photo.id: photo
        for photo in photos
    }

    for item in order_data:
        photo = photos_dict.get(item["id"])

        if photo:
            photo.order = item["order"]

    Photo.objects.bulk_update(
        photos,
        ["order"]
    )