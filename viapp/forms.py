from django import forms

from .models import Album, Photo


class AlbumForm(forms.ModelForm):
	class Meta:
		model = Album
		fields = ['title', 'description']

class MultipleFileInput(forms.ClearableFileInput):
	allow_multiple_selected = True

class MultipleFileField(forms.FileField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault("widget", MultipleFileInput())
		super().__init__(*args, **kwargs)

	def clean(self, data, initial = None):
		return(super().clean(file, initial) for file in data)

class PhotoForm(forms.ModelForm):
	images = MultipleFileField(label = "Фотографии")

	class Meta:
		model = Photo
		fields = []



