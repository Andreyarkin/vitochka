from http.client import responses

import pytest

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from viapp.models import Album, Photo
from viapp.views import albums
from viapp.services import view_and_download, edit_content, can_create_album, view_albums

User = get_user_model()

'''
Тесты views.py
'''

'''
Тесты функции albums
'''

# Тест перенаправления на log in если unlogged
@pytest.mark.django_db
def test_albums_requires_login(client):
    response = client.get('/albums/')
    assert response.status_code == 302

# текст если logged то открывает список альбомов
@pytest.mark.django_db
def test_albums_logged_in_ok(client, django_user_model):
    user = django_user_model.objects.create_user(
	    username='user', password='123')
    client.force_login(user)

    response = client.get('/albums/')
    assert response.status_code == 200

# Тест, что контекст содержит альбомы
@pytest.mark.django_db
def test_album_context_contain_albums(client, django_user_model):
    user = django_user_model.objects.create_user(username='Petr', password='123')
    client.force_login(user)

    response = client.get('/albums/')

    assert 'albums' in response.context

# Пользователь видит контекст
@pytest.mark.django_db
def test_albums_returns_user_albums(client, django_user_model):
    user = django_user_model.objects.create_user(username='Natan', password='123')
    client.force_login(user)

    album = Album.objects.create(title='test1', owner=user)

    response = client.get('/albums/')

    assert album in response.context['albums']

# Пользователь без прав создания альбома не видит контекст
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

# Тест пользователь с правом can_create_album видит контекст
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
@pytest.mark.django_db
def test_404_if_no_album(client, django_user_model):
    user_test = django_user_model.objects.create_user(username='Bob', password='123')
    client.force_login(user_test)

    response = client.get(f'/albums/99999999999/')

    assert response.status_code == 404

'''
Тесты функции photo
'''

# тест - нет фото - 404
@pytest.mark.django_db
def test_no_photo_404(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='Henry',
        password='123'
    )
    client.force_login(user)
    response = client.get(f'/album/99999999999/')

    assert response.status_code == 404

# тест владелец альбома может открыть фото
@pytest.mark.django_db
def test_owner_see_photo(client, django_user_model):
    user_owner = django_user_model.objects.create_user(
        username='Henry',
        password='123'
    )
    client.force_login(user_owner)

    album_1 = Album.objects.create(title='test4', owner=user_owner)
    photo_1 = Photo.objects.create(album=album_1, image='photos/1' )

    response = client.get(f'/album/{photo_1.id}/')

    assert response.status_code == 200
    assert response.context['photo'] == photo_1

# тест админ может открыть фото
@pytest.mark.django_db
def test_admin_see_photo(client, django_user_model):
    user_owner = django_user_model.objects.create_user(
        username='Henry',
        password='123'
    )
    user_admin = django_user_model.objects.create_superuser(
        username='Adam',
        password='123'
    )
    client.force_login(user_admin)

    album_1 = Album.objects.create(title='test4', owner=user_owner)
    photo_1 = Photo.objects.create(album=album_1, image='photos/1' )

    response = client.get(f'/album/{photo_1.id}/')

    assert response.status_code == 200
    assert response.context['photo'] == photo_1

# тест shared_with может открыть фото
@pytest.mark.django_db
def test_shared_see_photo(client, django_user_model):
    user_owner = django_user_model.objects.create_user(
        username='Henry',
        password='123'
    )
    user_shared = django_user_model.objects.create_user(
        username='Maga',
        password='123'
    )
    client.force_login(user_shared)

    album_1 = Album.objects.create(title='test4', owner=user_owner)
    photo_1 = Photo.objects.create(album=album_1, image='photos/1' )

    album_1.shared_with.add(user_shared)

    response = client.get(f'/album/{photo_1.id}/')

    assert response.status_code == 200
    assert response.context['photo'] == photo_1

# тест другой не может открыть фото
@pytest.mark.django_db
def test_other_cannot_see_photo(client, django_user_model):
    user_owner = django_user_model.objects.create_user(
        username='Henry',
        password='123'
    )
    user_other = django_user_model.objects.create_user(
        username='Hank',
        password='123'
    )
    client.force_login(user_other)

    album_1 = Album.objects.create(title='test4', owner=user_owner)
    photo_1 = Photo.objects.create(album=album_1, image='photos/1' )

    response = client.get(f'/album/{photo_1.id}/')

    assert response.status_code == 403

# незарегистрированный перенаправляется на log in
@pytest.mark.django_db
def test_unlogged_redirect(client, django_user_model):
    user_owner = django_user_model.objects.create_user(
        username='Henry',
        password='123'
    )
    album_1 = Album.objects.create(title='test4', owner=user_owner)
    photo_1 = Photo.objects.create(album=album_1, image='photos/1' )

    response = client.get(f'/album/{photo_1.id}/')

    assert response.status_code == 302

'''
Тесты функции add_album
'''

# тест can_create_album=True → создаётся альбом
@pytest.mark.django_db
def test_can_create_album_create_album(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='Henry',
        password='123',
        can_create_album=True
    )
    client.force_login(user)

    response = client.post('/add_album/', {'title': 'pytest album'})

    # Проверка на редирект
    assert response.status_code == 302
    # Проверка, что альбом создался
    assert  Album.objects.count() == 1
    album = Album.objects.first()
    # Проверка owner тот кто создал альбом
    assert album.owner == user
    assert album.title == 'pytest album'

# тест can_create_album=False → 403
@pytest.mark.django_db
def test_no_can_create_album_cannot_create_album(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='Nick',
        password='123',
        can_create_album=False
    )
    client.force_login(user)
    response = client.post('/add_album/', {'title': 'My album'})
    assert response.status_code == 403

'''
Тесты функции add_photo
'''

# Тест edit_content → может добавить
@pytest.mark.django_db
def test_if_edit_content_can_add_photo(client, django_user_model):
    user_owner = django_user_model.objects.create_user(
        username='Simon',
        password='123'
    )
    client.force_login(user_owner)

    album_1 = Album.objects.create(title = 'test7', owner = user_owner)

    image_1 = SimpleUploadedFile(
        name='Photo_1.jpg',
        content=b'file_content',
        content_type='image/jpeg'
    )

    url = reverse('viapp:add_photo', args=[album_1.id])
    response = client.post(url, {
        'title': 'Photo',
        'description': 'desc',
        'images': [image_1]
    })

    assert response.status_code == 302
    assert Photo.objects.count() == 1

    photo = Photo.objects.first()
    assert photo.album == album_1

# no permission → нельзя добавить
@pytest.mark.django_db
def test_no_permission_cannot_add_photo(client, django_user_model):
    user_owner = django_user_model.objects.create_user(
        username='Simon',
        password='123'
    )
    user_other = django_user_model.objects.create_user(
        username='Andrew',
        password='123'
    )
    client.force_login(user_other)

    album_1 = Album.objects.create(title = 'test7', owner = user_owner)

    image_1 = SimpleUploadedFile(
        name='Photo_1.jpg',
        content=b'file_content',
        content_type='image/jpeg'
    )

    url = reverse('viapp:add_photo', args=[album_1.id])
    response = client.post(url, {
        'title': 'Photo',
        'description': 'desc',
        'images': [image_1]
    })

    assert response.status_code == 403

# Тест пользователь загружает 3 картинки - создается 3 фото
@pytest.mark.django_db
def test_user_upload_three_image(client,django_user_model):
    user_owner = django_user_model.objects.create_user(username='Alfred', password='123')
    client.force_login(user_owner)

    album_3 = Album.objects.create(title='album_test', owner = user_owner)

    image_1 = SimpleUploadedFile(
        name='Photo_1.jpg',
        content=b'file_content',
        content_type='image/jpeg'
    )
    image_2 = SimpleUploadedFile(
        name='Photo_2.jpg',
        content=b'file_content',
        content_type='image/jpeg'
    )
    image_3 = SimpleUploadedFile(
        name='Photo_3.jpg',
        content=b'file_content',
        content_type='image/jpeg'
    )

    url = reverse('viapp:add_photo', args=[album_3.id])
    response = client.post(url, {
        'title':'photo 1',
        'description':'des',
        'images':[image_1, image_2, image_3]
    })

    assert response.status_code == 302
    assert Photo.objects.count() == 3

    for photo in Photo.objects.all():
        assert photo.album == album_3

# Тест фото не передается, форма невалидна
@pytest.mark.django_db
def test_test_user_cannot_upload_without_images(client, django_user_model):
    user_owner = django_user_model.objects.create_user(username='Mitchel', password='123')
    client.force_login(user_owner)

    album_4 = Album.objects.create(title='album_test', owner=user_owner)
    url = reverse('viapp:add_photo', args=[album_4.id])

    response = client.post(url, {
        'title': 'photo 4',
        'description': 'des',
        'images':[]
    })

    assert response.status_code == 200
    assert Photo.objects.count() == 0
    assert 'form' in response.context
    assert response.context['form'].errors

'''
Тесты функции delete_photo
'''

# owner - удаляет
@pytest.mark.django_db
def test_owner_can_delete(client, django_user_model):
    user_owner = django_user_model.objects.create_user(
        username='Bred',
        password='123'
    )
    client.force_login(user_owner)

    album_2 = Album.objects.create(title = 'test11', owner = user_owner)

    image_2 = SimpleUploadedFile(
        name='Photo_2.jpg',
        content=b'file_content',
        content_type='image/jpeg'
    )

    photo_2 = Photo.objects.create(album = album_2, image = image_2)

    url = reverse('viapp:delete_photo', args=[photo_2.id])

    response = client.post(url)
    assert response.status_code == 302
    assert Photo.objects.count() == 0

