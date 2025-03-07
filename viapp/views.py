from django.shortcuts import render
from .models import Album

# Create your views here.
def index(request):
    """Домашняя страница приложения"""
    return render(request, 'viapp/index.html')

def albums(request):
    # выводит список альбомов
    albums = Album.objects.all().order_by('-created_at')
    context = {'albums': albums}
    return render(request, 'viapp/albums.html', {'albums': albums})

def album(request):
    # страница альбома
    albums = Album.objects.all().order_by('-created_at')
    return render(request, 'viapp/album.html', {'albums': albums})

def photo(request, pk):
    #страница фотографии
    album = Album.objects.get(pk=pk)
    return render(request, 'viapp/photo.html', {'album': album})
