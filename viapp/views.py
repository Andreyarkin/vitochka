from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model

import json

from .models import Album, Photo
from .forms import AlbumForm, PhotoForm
from .services import (view_albums,
                       view_and_download,
                       can_create_album,
                       edit_content,
                       download_album_zip,
                       download_photofile,
                       delete_several_photos,
                       set_album_cover,
                       share_album_service,
                       reorder_photos)

""" 
права доступа безопасности:
A - admin
O - owner
C - can_create_album
S - shared_with
L - logged
U - unlogged
"""


# Create your views here.
def index(request):
	"""Домашняя страница приложения"""
	return render(request, 'viapp/index.html')


# выводит список альбомов
@login_required
def albums(request):
	# Безопасность (L and (A (видит всё) or (O or S (видят свое))))
	albums = view_albums(request.user)
	
	context = {
		'albums': albums,
		'can_create_album': can_create_album(request.user),
	}
	return render(request, 'viapp/albums.html', context)


# Страница альбома. Выводит альбом и фотографии в нем содержащиеся
@login_required
def album(request, album_id):
	album = get_object_or_404(Album, id=album_id)
	
	# Безопасность (A or O or S)
	if not view_and_download(request.user, album):
		raise PermissionDenied()
	
	photo = album.photos.order_by('-uploaded_at')
	
	context = {
		'album': album,
		'photo': photo,
		'edit_content': edit_content(request.user, album),
		'view_and_download': view_and_download(request.user, album)
	}
	
	return render(request, 'viapp/album.html', context)


@login_required
def photo(request, photo_id):
	# страница фотографии
	photo = get_object_or_404(Photo, id=photo_id)
	album = photo.album
	
	# Безопасность (A or O or S)
	if not view_and_download(request.user, album):
		raise PermissionDenied()
	
	# Все фото в альбоме отсортированные по ID
	all_photos = Photo.objects.filter(album=album).order_by('order')
	
	# Находим текущий индекс фото в списке
	photo_list = list(all_photos)
	current_index = photo_list.index(photo)
	
	# Следующее фото
	next_photo = photo_list[current_index + 1] if current_index + 1 < len(photo_list) else None
	
	# Предыдущее фото
	prev_photo = photo_list[current_index - 1] if current_index - 1 >= 0 else None
	
	context = {'photo': photo,
	           'next_photo': next_photo,
	           'prev_photo': prev_photo,
	           'edit_content': edit_content(request.user, album),
	           'view_and_download': view_and_download(request.user, album),
	           }
	
	return render(request, 'viapp/photo.html', context)


# функция добавления альбома
@login_required
def add_album(request):
	# Безопасность (A or C)
	if not can_create_album(request.user):
		raise PermissionDenied()
	
	# Страница добавления альбома
	if request.method != 'POST':
		form = AlbumForm()
	else:
		form = AlbumForm(data=request.POST)
		if form.is_valid():
			add_album = form.save(commit=False)
			add_album.owner = request.user
			add_album.save()
			return redirect('viapp:albums')
	
	context = {'form': form}
	return render(request, 'viapp/add_album.html', context)


# функция добавления фотографий
@login_required
def add_photo(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    if not edit_content(request.user, album):
        raise PermissionDenied()

    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)

        if form.is_valid():
            images = form.cleaned_data['images']

            if not images:
                form.add_error('images', 'Добавьте хотя бы одно фото')
            else:
                for image in images:
                    Photo.objects.create(
                        album=album,
                        image=image
                    )

                return redirect('viapp:album', album_id=album.id)

    else:
        form = PhotoForm()

    return render(request, 'viapp/add_photo.html', {
        'form': form,
        'album': album
    })


# Функция загрузки фото
@login_required
def download_photo(request, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	album = photo.album
	
	# Безопасность (A or O or S)
	if not view_and_download(request.user, album):
		raise PermissionDenied()
	
	return download_photofile(photo)


# Функция удаления фото
@login_required
def delete_photo(request, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	album = photo.album
	
	# Безопасность (A or O)
	if not edit_content(request.user, album):
		raise PermissionDenied()
	
	album_id = album.id
	photo.delete()
	return redirect('viapp:album', album_id=album_id)


# Функция загрузки альбома
@login_required
def download_album(request, album_id):
	album = get_object_or_404(Album, id=album_id)
	
	# Безопасность (A or O or S)
	if not view_and_download(request.user, album):
		raise PermissionDenied()
	
	zip_buffer = download_album_zip(album)
	response = HttpResponse(zip_buffer, content_type='application/zip')
	response['Content-Disposition'] = f'attachment; filename = "{album.title}.zip"'
	return response


# Функция удаления альбома
@login_required
def delete_album(request, album_id):
	album = get_object_or_404(Album, id=album_id)
	
	# Безопасность (A or O)
	if not edit_content(request.user, album):
		raise PermissionDenied()
	
	album.delete()
	return redirect('viapp:albums')


# Функция удаления выбранных фото
@login_required
def delete_selected_photos(request, album_id):
	album = get_object_or_404(Album, id=album_id)
	
	if request.method == 'POST':
		photo_ids = request.POST.getlist('photo_ids')
		if photo_ids:
			delete_several_photos(request.user, photo_ids, album=album)
	
	return redirect('viapp:album', album_id=album.id)


# Функция выбора обложки альбома
@login_required
def select_cover(request, album_id, photo_id):
	album = get_object_or_404(Album, id=album_id)
	photo = get_object_or_404(Photo, id=photo_id)
	
	set_album_cover(request.user, album, photo)
	
	return redirect('viapp:album', album_id=album.id)


# Функция обновления порядка фотографий
@login_required
def update_photo_order(request):
	if request.method != 'POST':
		return JsonResponse({'status': 'error'}, status=405)
	
	try:
		data = json.loads(request.body)
		
		if not data:
			raise PermissionDenied()
		
		photo_id = data[0]["id"]
		
		photo = get_object_or_404(Photo, id=photo_id)
		
		album = photo.album
		
		reorder_photos(
			request.user,
			album,
			data
		)
		
		return JsonResponse({'status': 'success'})
	
	except Exception as e:
		return JsonResponse(
			{'status': 'error', 'message': str(e)},
			status=400
		)


@login_required
def share_album(request, album_id):
	album = get_object_or_404(Album, id=album_id)
	
	if request.method == "POST":
		user_ids = request.POST.getlist("users")
		User = get_user_model()
		users = User.objects.filter(id__in=user_ids)
		share_album_service(request.user, album, users)
		return redirect("viapp:album", album_id=album.id)
	
	# Используем кастомного пользователя
	User = get_user_model()
	users = User.objects.exclude(id=request.user.id)
	return render(request, "viapp/share_album.html", {"album": album, "users": users})
