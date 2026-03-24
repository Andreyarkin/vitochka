from django.db.models import Q
from .models import Album


def get_user_albums(user):
    """
    Возвращает queryset альбомов, доступных пользователю
    """

    # Неавторизованный пользователь — ничего не видит
    if not user.is_authenticated:
        return Album.objects.none()

    # Суперпользователь — видит всё
    if user.is_superuser:
        return Album.objects.all()

    # Обычный пользователь — свои + расшаренные
    return Album.objects.filter(
        Q(owner=user) | Q(shared_with=user)
    ).distinct()