from django.db.models import Q
from .models import Album



def can_view_albums(user):
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

def can_view_album(user, album):
    return (
        user.is_superuser or
        album.owner == user or
        user in album.shared_with.all()
    )

def can_create_album(user):
    return user.is_superuser or user.can_create_album

def edit_content (user, album):
    return (
        user.is_superuser or
        album.owner == user
    )


