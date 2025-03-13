from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.exceptions import PermissionDenied


from .models import Album, Photo
from .forms import AlbumForm, PhotoForm

# Create your views here.
def index(request):
	"""Домашняя страница приложения"""
	return render(request, 'viapp/index.html')

@login_required()
def albums(request):
	# выводит список альбомов
	albums = Album.objects.filter(owner = request.user).order_by('-created_at')
	context = {'albums': albums}
	return render(request, 'viapp/albums.html', context)

@login_required()
def album(request, album_id):
	# страница альбома. Выводит альбом и фотографии в нем содержащиеся
	album = Album.objects.get(id = album_id)
	# Проверка того, что тема принадлежит текущему пользователю.
	if album.owner != request.user:
		raise PermissionDenied()
	photo = album.photos.order_by('-uploaded_at')
	context = {'album':album, 'photo':photo}
	return render(request, 'viapp/album.html', context)

@login_required()
def photo(request, photo_id):
	#страница фотографии
	photo = Photo.objects.get(id = photo_id)
	context = {'photo':photo}
	return render(request, 'viapp/photo.html', context)

@login_required()
def add_album(request):
	# Страница добавления альбома
	if request.method != 'POST':
		form = AlbumForm()
	else:
		form = AlbumForm(data = request.POST)
		if form.is_valid():
			add_album = form.save(commit=False)
			add_album.owner = request.user
			add_album.save()
			return redirect ('viapp:albums')
	context = {'form' : form}
	return render(request, 'viapp/add_album.html', context)

@login_required()
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







