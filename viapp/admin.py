from django.contrib import admin
from .models import Album
from .models import Photo

# Register your models here.
admin.site.register(Album)
admin.site.register(Photo)

