import pytest

from django.contrib.auth import get_user_model

from viapp.models import Album
from viapp.views import albums
from viapp.services import view_and_download, edit_content, can_create_album, view_albums

User = get_user_model()

'''
Тесты views.py
'''

'''
Тесты функции albums
'''

# Тест альбомы выводятся
@pytest.mark.django_db
def test_albums_requires_login(client):
    response = client.get('/albums/')
    assert response.status_code == 302

@pytest.mark.django_db
def test_albums_logged_in_ok(client, django_user_model):
    user = django_user_model.objects.create_user(
	    username='user', password='123')
    client.force_login(user)

    response = client.get('/albums/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_album_context_contain_albums(client, django_user_model):
    user = django_user_model.objects.create_user(username='Petr', password='123')
    client.force_login(user)

    response = client.get('/albums/')

    assert 'albums' in response.context

@pytest.mark.django_db
def test_albums_returns_user_albums(client, django_user_model):
    user = django_user_model.objects.create_user(username='Natan', password='123')
    client.force_login(user)

    album = Album.objects.create(title='test1', owner=user)

    response = client.get('/albums/')

    assert album in response.context['albums']

@pytest.mark.django_db
def test_user_cannot_create_album_has_no_context(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='Nick',
        password='123',
        can_create_album=False
    )
    client.force_login(user)

    response = client.get('/albums/')

    assert response.context['can_create_album'] is False

@pytest.mark.django_db
def test_user_can_create_album_has_context(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='Nick',
        password='123',
        can_create_album=True
    )
    client.force_login(user)

    response = client.get('/albums/')

    assert response.status_code == 200
    assert response.context['can_create_album'] is True

'''
Тесты функции album
'''

# Владелец может открыть альбом
@pytest.mark.django_db
def test_owner_can_view_album(client, django_user_model):
    user_owner = django_user_model.objects.create_user(username='Tim', password='123')
    client.force_login(user_owner)

    album = Album.objects.create(title='test3', owner=user_owner)
    response = client.get(f'/albums/{album.id}/')

    assert response.status_code == 200
    assert response.context['album'] == album

# Другой пользователь не может открыть альбом
@pytest.mark.django_db
def test_other_cannot_view_album(client, django_user_model):
    user_owner = django_user_model.objects.create_user(username='Tim', password='123')
    user_other = django_user_model.objects.create_user(username='Misha', password='123')
    client.force_login(user_other)

    album = Album.objects.create(title='test3', owner=user_owner)
    response = client.get(f'/albums/{album.id}/')

    assert response.status_code == 403

# неавторизованный перенаправляется на log in (302)
@pytest.mark.django_db
def test_album_requires_login(client, django_user_model):
    user_owner = django_user_model.objects.create_user(username='Tim', password='123')
    album = Album.objects.create(title='test3', owner=user_owner)
    response = client.get(f'/albums/{album.id}/')
    assert response.status_code == 302

# Пользователь из shared_with может открыть альбом
@pytest.mark.django_db
def test_user_shared_with_can_view_album(client, django_user_model):
    user_owner = django_user_model.objects.create_user(username='Tim', password='123')
    user_shared = django_user_model.objects.create_user(username='Sam', password='123')

    album = Album.objects.create(title='test3', owner=user_owner)
    album.shared_with.add(user_shared)

    client.force_login(user_shared)

    response = client.get(f'/albums/{album.id}/')

    assert response.status_code == 200
    assert response.context['album'] == album

# Проверить работу 404 если альбома нету
def test_404_if_no_album(client, django_user_model):
    user_test = django_user_model.objects.create_user(username='Bob', password='123')
    client.force_login(user_test)

    response = client.get(f'/albums/99999999999/')

    assert response.status_code == 404






