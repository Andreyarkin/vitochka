from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from io import BytesIO

import zipfile
import os

from viapp.models import Photo
from viapp.API.serializers import AlbumSerializer, PhotoSerializer
from viapp.API.permissions import IsOwnerOrSharedOrAdmin
from viapp.services import view_albums, view_and_download

User = get_user_model()

class AlbumViewSet(ModelViewSet):
	serializer_class = AlbumSerializer
	permission_classes = [IsAuthenticated, IsOwnerOrSharedOrAdmin]

	def get_queryset(self):
		return view_albums(self.request.user)

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)

	# Скачать альбом
	@action(detail=True, methods=['get'])
	def download(self, request, pk=None):
		album = self.get_object()
		
		if not view_and_download(request.user, album):
			return Response({"error": "Нет доступа"}, status=403)
		
		zip_buffer = BytesIO()
		
		with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
			for photo in album.photos.all():
				photo_path = photo.image.path
				if os.path.exists(photo_path):
					zip_file.write(photo_path, os.path.basename(photo_path))
		
		zip_buffer.seek(0)
		
		response = HttpResponse(zip_buffer, content_type='application/zip')
		response['Content-Disposition'] = f'attachment; filename="{album.title}.zip"'
		
		return response




	# Поделится альбомом
	@action(detail=True, methods=['post'])
	def share(self, request, pk=None):
		album = self.get_object()
		user_id = request.data.get("user_id")

		user = get_object_or_404(User, id=user_id)
		album.shared_with.add(user)

		return Response({"status": "Пользователь добавлен"})

	# Установить обложку
	@action(detail=True, methods=['post'])
	def set_cover(self, request, pk=None):
		album = self.get_object()
		photo_id = request.data.get("photo_id")

		photo = get_object_or_404(Photo, id=photo_id, album=album)
		album.cover = photo
		album.save()

		return Response({"status": "Обложка обновлена"})

	# Изменить порядок фото
	@action(detail=True, methods=['post'])
	def reorder(self, request, pk=None):
		album = self.get_object()
		order = request.data.get("order", [])

		for index, photo_id in enumerate(order):
			Photo.objects.filter(id=photo_id, album=album).update(order=index)

		return Response({"status": "Порядок обновлён"})

	# для привязки фото к альбому
	@action(detail=True, methods=['get'])
	def photos(self, request, pk=None):
		album = self.get_object()

		photos = Photo.objects.filter(album=album)
		serializer = PhotoSerializer(photos, many=True)
		return Response(serializer.data)

class PhotoViewSet(ModelViewSet):
	serializer_class = PhotoSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Photo.objects.filter(album__in=view_albums(user))

	@action(detail=True, methods=['get'])
	def download(self, request, pk=None):
		photo = self.get_object()

		if not view_and_download(request.user, photo.album):
			return Response({"error": "Нет доступа"}, status=403)

		return Response({"status": f"Скачивание фото {photo.id}"})

	@action(detail=False, methods=['post'])
	def many_delete(self, request):
		ids = request.data.get("ids", [])

		photos = Photo.objects.filter(
			id__in=ids,
			album__in=view_albums(request.user),
		)
		count = photos.count()
		photos.delete()

		return Response({"deleted": count})
