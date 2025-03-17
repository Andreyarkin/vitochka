from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse


from .models import Album, Photo
from .forms import AlbumForm, PhotoForm

# проверка того, является ли пользователь администратором
def admin_required(view_func):
    """Декоратор для проверки прав суперпользователя."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Доступ запрещён.")
        return view_func(request, *args, **kwargs)
    return wrapper

# Create your views here.
def index(request):
	"""Домашняя страница приложения"""
	return render(request, 'viapp/index.html')

@login_required()
def albums(request):
	# выводит список альбомов
	if request.user.is_superuser:
		albums = Album.objects.all().order_by('-created_at')
	else:
		albums = Album.objects.filter(owner = request.user).order_by('-created_at')
	context = {'albums': albums}
	return render(request, 'viapp/albums.html', context)

@login_required()
def album(request, album_id):
	# страница альбома. Выводит альбом и фотографии в нем содержащиеся
	album = Album.objects.get(id = album_id)
	# Проверка того, что альбом принадлежит текущему пользователю.
	if not request.user.is_superuser and album.owner != request.user:
		raise PermissionDenied()
	photo = album.photos.order_by('-uploaded_at')
	context = {'album':album, 'photo':photo}
	return render(request, 'viapp/album.html', context)

@login_required()
def photo(request, photo_id):
	#страница фотографии
	photo = Photo.objects.get(id = photo_id)
	# Проверка того, что фото принадлежит текущему пользователю.
	if not request.user.is_superuser and photo.album.owner != request.user:
		raise PermissionDenied()
	context = {'photo':photo}
	return render(request, 'viapp/photo.html', context)

# функция добавления альбома
@login_required()
@admin_required
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

# функция добавления фотографии
@login_required()
@admin_required
def add_photo(request):
	# Страница добавления фотографии
	if request.method != 'POST':
		form = PhotoForm()
	else:
		form = PhotoForm(data = request.POST, files=request.FILES)
		if form.is_valid():
			photo_add = form.save()
			photo_add.album.owner = request.user
			photo_add.save()
			return redirect ('viapp:album', album_id=photo_add.album.id)
		else:
			print(form.errors)
	context = {'form' : form}
	return render(request, 'viapp/add_photo.html', context)

# Функция загрузки фото
@login_required()
def download_photo(request, photo_id):
	photo = Photo.objects.get(id = photo_id)
	if not request.user.is_superuser and photo.album.owner != request.user:
		raise PermissionDenied()
	else:
		file = open(photo.image.path, 'rb')
		response = FileResponse(file)

	# Имя файла для скачивания
	response['Content-Disposition'] = f'attachment; filename = "{photo.image.name}"'
	return response









