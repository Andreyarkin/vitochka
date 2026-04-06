from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
	add_form = CustomUserCreationForm
	form = CustomUserChangeForm
	model = CustomUser
	list_display = ['email', 'username']

	# Дополнительное поле "может ли создавать альбомы"
	fieldsets = UserAdmin.fieldsets + (
		('Дополнительные права', {
			'fields': ('can_create_album',),
		}),
	)

admin.site.register(CustomUser, CustomUserAdmin)
