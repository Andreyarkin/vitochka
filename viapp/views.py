from django.shortcuts import render, redirect
from .models import Album, Photo
from .forms import AlbumForm, PhotoForm

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

def add_album(request):
	# Страница добавления альбома
	if request.method != 'POST':
		form = AlbumForm()
	else:
		form = AlbumForm(data = request.POST)
		if form.is_valid():
			form.save()
			return redirect ('viapp:albums')
	context = {'form' : form}
	return render(request, 'viapp/add_album.html', context)

def add_photo(request):
	# Страница добавления фотографии
	if request.method != 'POST':
		form = PhotoForm()
	else:
		form = PhotoForm(data = request.POST, files=request.FILES)
		if form.is_valid():
			photo = form.save()
			return redirect ('viapp:album', album_id=photo.album.id)
		else:
			print(form.errors)
	context = {'form' : form}
	return render(request, 'viapp/add_photo.html', context)







