from django.contrib import admin

from .models import Album
from .models import Photo

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at")
    search_fields = ("title", "description")
    list_filter = ("created_at",)
    filter_horizontal = ("shared_with",)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "album", "uploaded_at", "order")
    search_fields = ("title", "description", "caption")
    list_filter = ("album", "uploaded_at")
    ordering = ("album", "order")

