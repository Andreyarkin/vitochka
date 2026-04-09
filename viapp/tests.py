import pytest

from django.contrib.auth import get_user_model

from viapp.models import Album
from viapp.services import view_and_download, edit_content, can_create_album

User = get_user_model()

'''
Тесты функции view_and_download (далее - видит)
'''

# Тест админ видит свой альбом
@pytest.mark.django_db
def test_admin_can_view_own_album():
    user_admin = User.objects.create_superuser(username='admin', password='123')
    album = Album.objects.create(title='Test album', owner=user_admin)
    result = view_and_download(user_admin, album)

    assert result is True

# Тест Owner видит свой альбом
@pytest.mark.django_db
def test_owner_can_view_own_album():
    user_owner = User.objects.create_user(username='user_owner', password='123')
    album = Album.objects.create(title='Test album', owner=user_owner)

    result = view_and_download(user_owner, album)

    assert result is True

# Тест Shared видит альбом с которым с ним поделились
@pytest.mark.django_db
def test_shared_user_can_view_album():
    user_owner = User.objects.create_user(username='user_owner', password='123')
    shared_user = User.objects.create_user(username='shared', password='123')

    album = Album.objects.create(title='Test album', owner=user_owner)
    album.shared_with.add(shared_user)

    result = view_and_download(shared_user, album)

    assert result is True

# Тест другой пользователь
@pytest.mark.django_db
def test_other_user_cannot_view_album():
    user_owner = User.objects.create_user(username='user_owner', password='123')
    user_other = User.objects.create_user(username='user_other', password='123')
    album = Album.objects.create(title='Test album', owner=user_owner)
    result = view_and_download(user_other, album)

    assert result is False

# Тест админ видит альбомы в которых он не owner
@pytest.mark.django_db
def test_admin_can_view_any_album():
    user_admin = User.objects.create_superuser(username='user_admin', password='123')
    user_owner = User.objects.create_user(username='owner', password='123')

    album = Album.objects.create(title='Test', owner=user_owner)

    assert view_and_download(user_admin, album) is True

'''
Тесты функции edit_content
'''

# Тест владелец может изменять данные
@pytest.mark.django_db
def test_only_owner_can_edit():
    user_owner = User.objects.create_user(username='user_owner', password='123')
    album = Album.objects.create(title='test_album', owner=user_owner)

    assert edit_content(user_owner, album) is True


# Тест НЕвладелец НЕ может изменять данные
@pytest.mark.django_db
def test_other_cannot_edit():
    user_owner = User.objects.create_user(username='user_owner', password='123')
    user_other = User.objects.create_user(username='user_other', password='123')

    album = Album.objects.create(title='test_album', owner=user_owner)

    assert edit_content(user_other, album) is False

# Тест админ может изменять данные
@pytest.mark.django_db
def test_admin_can_edit():
    user_owner = User.objects.create_user(username='user_owner', password='123')
    user_admin = User.objects.create_superuser(username='user_admin', password='123')

    album = Album.objects.create(title='test_album', owner=user_owner)

    assert edit_content(user_admin, album) is True

'''
Тесты функции can_create_album
'''

# Тест админ может создать альбом
@pytest.mark.django_db
def test_admin_can_create_album():
    user_admin = User.objects.create_superuser(username='Andrey', password='123')

    assert can_create_album(user_admin) is True

# Тест пользователь с правами создания может создать альбом
@pytest.mark.django_db
def test_user_can_create_can_create_album():
    user_can_create = User.objects.create_user(
        username='can_create',
        password='123',
        can_create_album=True
    )

    assert can_create_album(user_can_create) is True

# Тест юзер без прав может создать альбом
@pytest.mark.django_db
def test_other_cannot_create_album():
    user_other = User.objects.create_user(username='other_user', password='123')

    assert can_create_album(user_other) is False
