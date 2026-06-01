from django import forms

from .models import Album, Photo


class AlbumForm(forms.ModelForm):
	class Meta:
		model = Album
		fields = ['title', 'description']

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
	widget = MultipleFileInput
	
	def clean(self, data, initial=None):
		if not data:
			return []
		
		files = data
		if not isinstance(files, (list, tuple)):
			files = [files]
		
		cleaned_files = []
		
		for file in files:
			file = super().clean(file, initial)
			
			# 🔥 проверка типа
			if file.content_type not in [
				'image/jpeg',
				'image/png',
				'image/webp'
			]:
				raise forms.ValidationError("Можно загружать только изображения формата jpeg, png, webp")
			
			# 🔥 размер
			if file.size > 20 * 1024 * 1024:
				raise forms.ValidationError("Файл слишком большой (max 20MB)")
			
			cleaned_files.append(file)
		
		return cleaned_files


class PhotoForm(forms.Form):
	images = MultipleFileField(label = "Фотографии")

	class Meta:
		model = Photo
		fields = []
