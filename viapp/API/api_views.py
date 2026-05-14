from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse, FileResponse

from viapp.models import Album, Photo
from viapp.API.serializers import AlbumSerializer, PhotoSerializer
from viapp.API.permissions import IsOwnerOrSharedOrAdmin
from viapp.services import (view_albums,
                            view_and_download,
                            download_album_zip,
                            download_photofile,
                            delete_several_photos,
                            set_album_cover,
                            share_album_service,
                            reorder_photos)

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
	def download_album(self, request, pk=None):
		album = self.get_object()
		
		if not view_and_download(request.user, album):
			return Response({"error": "Нет доступа"}, status=403)
		
		zip_buffer = download_album_zip(album)
		
		response = HttpResponse(zip_buffer, content_type='application/zip')
		response['Content-Disposition'] = f'attachment; filename="{album.title}.zip"'
		
		return response

	# Поделится альбомом
	@action(detail=True, methods=['post'])
	def share_album(self, request, pk=None):
		album = self.get_object()
		user_ids = request.data.get("shared_with", [])

		users = User.objects.filter(id__in=user_ids)
		share_album_service(request.user, album, users)

		return Response({"status": "Доступ обновлен"})

	# Установить обложку
	@action(detail=True, methods=['post'])
	def set_album_cover(self, request, pk=None):
		album = self.get_object()
		photo_id = request.data.get("photo_id")
		photo = get_object_or_404(Photo, id=photo_id)
		
		set_album_cover(request.user, album, photo)

		return Response({"status": "Обложка обновлена"})

	# Изменить порядок фото
	@action(detail=True, methods=['post'])
	def reorder_photos(self, request, pk=None):
		album = self.get_object()
		
		order_data = request.data.get("order", [])
		
		reorder_photos(
			request.user,
			album,
			order_data
		)
		
		return Response({"status": "Порядок обновлён"})

	# для привязки фото к альбому
	@action(detail=True, methods=['get'])
	def photo_list(self, request, pk=None):
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
	def download_photo(self, request, pk=None):
		photo = self.get_object()

		if not view_and_download(request.user, photo.album):
			return Response({"error": "Нет доступа"}, status=403)

		return download_photofile(photo)
	
	@action(detail=False, methods=['post'])
	def many_photo_delete(self, request):
		ids = request.data.get("ids", [])
		album_id = request.data.get("album_id")
		album = get_object_or_404(Album, id=album_id)

		count = delete_several_photos(request.user, ids, album)

		return Response({"deleted": count})
