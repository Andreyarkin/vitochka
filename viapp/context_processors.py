from django.db.models import Q
from .models import Album

def albums_list(request):
    # Если пользователь не авторизован — возвращаем пустой список
    if not request.user.is_authenticated:
        return {'albums': []}

    # Если суперпользователь — видит все альбомы
    if request.user.is_superuser:
        albums = Album.objects.all()
    else:
        # Обычный пользователь — только свои и расшаренные
        albums = Album.objects.filter(
            Q(owner=request.user) | Q(shared_with=request.user)
        ).distinct()

    return {'albums': albums}