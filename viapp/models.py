from django.db import models
from django.conf import settings


class Album(models.Model):
	# Альбом для просмотра фотографий
	title = models.CharField(max_length=100, verbose_name="Название альбома")
	description = models.TextField(blank=True, default="Без описания", verbose_name="Описание альбома")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
	shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="shared_albums",
	                                     verbose_name="Доступ для пользователей")
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="albums")
	cover = models.ForeignKey(
		'Photo',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		verbose_name="Обложка альбома",
		related_name="cover_for_albums"
	)

	def __str__(self):
		return self.title

	class Meta():
		verbose_name = "Альбом"
		verbose_name_plural = "Альбомы"

class Photo(models.Model):
	title = models.CharField(max_length=100, null=True, blank=True, verbose_name="Название фотографии")
	description = models.TextField(blank=True, verbose_name="Описание фотографии")
	album = models.ForeignKey(Album, related_name="photos", on_delete=models.CASCADE, verbose_name="Альбом")
	image = models.ImageField(upload_to='photos/', verbose_name=" Фотография")
	caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="Подпись")
	uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
	order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

	def __str__(self):
		return f"{self.title} - альбом: {self.album.title}"

	class Meta:
		verbose_name = "Фотография"
		verbose_name_plural = "Фотографии"
		ordering = ['order'] # сортировка по умолчанию
