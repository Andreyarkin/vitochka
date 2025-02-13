from django.db import models

class Album(models.Model):
    #Альбом для просмотра фотографий
    title = models.CharField(max_length=255, verbose_name="Название альбома")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta():
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"

class Photo(models.Model):
    album = models.ForeignKey(Album, related_name="photos", on_delete=models.CASCADE, verbose_name="Альбом")
    image = models.ImageField(upload_to='photos/', verbose_name="Изображение")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="Подпись")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    def __str__(self):
        return f"Фото из альбома: {self.album.title}"

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"