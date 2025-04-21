from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponse, JsonResponse

import zipfile
import os
import json

from io import BytesIO

from .models import Album, Photo
from .forms import AlbumForm, PhotoForm

# декоратор - проверка того, является ли пользователь администратором
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
	album = photo.album

	# Все фото в альбоме отсортированные по ID
	all_photos = Photo.objects.filter(album=album).order_by('id')

	# Находим текущий индекс фото в списке
	photo_list = list(all_photos)
	current_index = photo_list.index(photo)

	# Следующее фото
	next_photo = photo_list[current_index+1] if current_index + 1 < len(photo_list) else None

	# Предыдущее фото
	prev_photo = photo_list[current_index-1] if current_index - 1 >= 0 else None

	# Проверка того, что фото принадлежит текущему пользователю.
	if not request.user.is_superuser and photo.album.owner != request.user:
		raise PermissionDenied()
	context = {'photo':photo,
				'next_photo': next_photo,
				'prev_photo': prev_photo,
				}
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

# функция добавления фотографий
@login_required()
@admin_required
def add_photo(request, album_id):
	album = Album.objects.get(id=album_id)

	if request.method != 'POST':
		form = PhotoForm(initial={'album': album})
	else:
		form = PhotoForm(request.POST, request.FILES)
		if form.is_valid():
			images = request.FILES.getlist('images')

			for image in images:
				Photo.objects.create(
					album = album,
					title = form.cleaned_data.get('title', ''),
					description = form.cleaned_data.get('description', ''),
					image = image
				)
			return redirect('viapp:album', album_id = album.id)

	context = {'form' : form, 'album': album}
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

# Функция удаления фото
@login_required()
def delete_photo(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	if not request.user.is_superuser and photo.album.owner != request.user:
		raise PermissionDenied()
	else:
		photo.delete()
		return redirect('viapp:album', album_id=photo.album.id)

# Функция загрузки альбома
def download_album(request, album_id):
	album = Album.objects.get(id = album_id)
	zip_buffer = BytesIO()
	with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
		for photo in album.photos.all():
			photo_path = photo.image.path
			if os.path.exists(photo_path):
				zip_file.write(photo_path, os.path.basename(photo_path))

	zip_buffer.seek(0)
	response = HttpResponse(zip_buffer, content_type='application/zip')
	response['Content-Disposition'] = f'attachment; filename = "{album.title}.zip"'
	return response

# Функция удаления альбома
def delete_album(request, album_id):
	album = Album.objects.get(id=album_id)
	if not request.user.is_superuser and photo.album.owner != request.user:
		raise PermissionDenied()
	else:
		album.delete()
		return redirect('viapp:albums')

# Функция удаления выбранных фото
def delete_selected_photos(request, album_id):
	album = Album.objects.get(id=album_id)

	# Проверка прав
	if not request.user.is_superuser and album.owner != request.user:
		raise PermissionDenied("У вас нет прав на удаление фотографий")

	if request.method == 'POST':
		photo_ids = request.POST.getlist('photo_ids')
		if photo_ids:
			# Удаляем только фотографии из текущего альбома
			Photo.objects.filter(
				id__in=photo_ids,
				album=album
			).delete()

		return redirect('viapp:album', album_id=album.id)

	return redirect('viapp:album', album_id=album.id)

# Функция выбора обложки альбома
@login_required
@admin_required
def select_cover(request, album_id, photo_id):
	album = Album.objects.get(id=album_id)
	photo = Photo.objects.get(id=photo_id)

	album.cover = photo
	album.save()
	return redirect('viapp:album', album_id=album.id)

# Функция обновления порядка фотографий
@login_required
@admin_required
def update_photo_order(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			for item in data:
				photo = Photo.objects.get(id=item['id'])
				photo.order = item['order']
				photo.save()
			return JsonResponse({'status': 'success'})
		except Exception as e:
			return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
	return JsonResponse({'status': 'error'}, status=405)







