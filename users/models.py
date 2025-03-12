from django.db import models
from django.contrib.auth.models import User, AbstractUser

class CustomUser(AbstractUser):
	pass
	#Добавить нужные поля тут

	def __str__(self):
		return self.username