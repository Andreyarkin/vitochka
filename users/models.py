from django.db import models
from django.contrib.auth.models import User, AbstractUser

class CustomUser(AbstractUser):
	can_create_album = models.BooleanField(default=False,
	                                       verbose_name="Может создавать альбомы"
	                                       )

	def __str__(self):
		return self.username