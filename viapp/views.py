from django.shortcuts import render
from .models import Album, Photo

# Create your views here.
def index(request):
    """Домашняя страница приложения"""
    return render(request, 'viapp/index.html')

def albums(request):
    # выводит список альбомов
    albums = Album.objects.all().order_by('-created_at')
    context = {'albums': albums}
    return render(request, 'viapp/albums.html', {'albums': albums})

def album(request, album_id):
    # страница альбома. Выводит альбом и фотографии в нем содержащиеся
    album = Album.objects.get(id = album_id)
    photo = album.photos.order_by('-uploaded_at')
    context = {'album':album, 'photo':photo}
    return render(request, 'viapp/album.html', context)

def photo(request, photo_id):
    #страница фотографии
    photo = Photo.objects.get(id = photo_id)
    context = {'photo':photo}
    return render(request, 'viapp/photo.html', context)
