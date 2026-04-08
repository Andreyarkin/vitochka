import pytest

from django.contrib.auth import get_user_model
from viapp.models import Album
from viapp.services import view_and_download

User = get_user_model()
