import pytest

from django.contrib.auth import get_user_model

from viapp.models import Album
from viapp.services import view_and_download, edit_content, can_create_album, view_albums

User = get_user_model()


'''
Тесты services.py
'''

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
def test_user_with_permission_can_create_album():
    user_can_create = User.objects.create_user(
        username='can_create',
        password='123',
        can_create_album=True
    )

    assert can_create_album(user_can_create) is True

# Тест юзер без прав не может создать альбом
@pytest.mark.django_db
def test_other_cannot_create_album():
    user_other = User.objects.create_user(username='other_user', password='123')

    assert can_create_album(user_other) is False

'''
Тесты функции view_albums
'''

# Пользователь незалогиген, ничего не видит
@pytest.mark.django_db
def test_anonymous_see_nothing():
    from django.contrib.auth.models import AnonymousUser
    anonymous_user = AnonymousUser()

    user_admin = User.objects.create_superuser(
        username='Andrey',
        password='123'
    )
    user_owner = User.objects.create_user(
        username='Dima',
        password='123',
    )

    album_1 = Album.objects.create(title='Album 1', owner=user_admin)
    album_2 = Album.objects.create(title='Album 2', owner=user_owner)

    result = view_albums(anonymous_user)

    assert result.count() == 0
    assert album_1 not in result
    assert album_2 not in result

# Пользователь админ и видит свои альбомы
@pytest.mark.django_db
def test_admin_see_own_albums():
    user_admin = User.objects.create_superuser(
        username='Andrey',
        password='123'
    )
    album_1 = Album.objects.create(title='Album 1', owner=user_admin)
    album_2 = Album.objects.create(title='Album 2', owner=user_admin)

    result = view_albums(user_admin)

    assert result.count() == 2
    assert album_1 in result
    assert album_2 in result

# Пользователь админ и видит чужие альбомы
@pytest.mark.django_db
def test_admin_see_others_albums():
    user_admin = User.objects.create_superuser(
        username='Andrey',
        password='123'
    )
    user_owner = User.objects.create_user(
        username='Dima',
        password='123',
    )
    album_1 = Album.objects.create(title='Album 1', owner=user_admin)
    album_2 = Album.objects.create(title='Album 2', owner=user_owner)

    result = view_albums(user_admin)

    assert result.count() == 2
    assert album_1 in result
    assert album_2 in result

# Пользователь owner видит свои
@pytest.mark.django_db
def test_owner_see_own_albums():
    user_owner = User.objects.create_user(
        username='Dima',
        password='123',
    )
    album_1 = Album.objects.create(title='Album 1', owner=user_owner)
    album_2 = Album.objects.create(title='Album 2', owner=user_owner)

    result = view_albums(user_owner)

    assert result.count() == 2
    assert album_1 in result
    assert album_2 in result


# Пользователь shared видит то че с ним поделились
@pytest.mark.django_db
def test_user_shared_see_shared_albums():
    user_owner = User.objects.create_user(
        username='Dima',
        password='123',
    )
    user_shared = User.objects.create_user(
        username='Anton',
        password='123',
    )
    album_1 = Album.objects.create(title='Album 1', owner=user_owner)
    album_2 = Album.objects.create(title='Album 2', owner=user_owner)
    
    album_1.shared_with.add(user_shared)
    album_2.shared_with.add(user_shared)

    result = view_albums(user_shared)

    assert result.count() == 2
    assert album_1 in result
    assert album_2 in result

# Пользователь видит альбомы в порядке order_by('created_at)
@pytest.mark.django_db
def test_albums_order_by_created_at():
    user = User.objects.create_user(username='user', password='123')
    album_1 = Album.objects.create(title='Album 1', owner=user)
    album_2 = Album.objects.create(title='Album 2', owner=user)

    result = list(view_albums(user))
    # Проверяем порядок по created_at
    assert result[0] == album_1
    assert result[1] == album_2

# проверка distinct()
@pytest.mark.django_db
def test_distinct():
    user_owner = User.objects.create_user(
        username='Dima',
        password='123',
    )
    user_shared = User.objects.create_user(
        username='Anton',
        password='123',
    )
    album_1 = Album.objects.create(title='Album 1', owner=user_owner)
    album_2 = Album.objects.create(title='Album 2', owner=user_owner)
    album_1.shared_with.add(user_shared)
    album_2.shared_with.add(user_shared)
    album_1.shared_with.add(user_owner)
    album_2.shared_with.add(user_owner)

    result = view_albums(user_shared)

    assert result.count() == 2
    assert album_1 in result
    assert album_2 in result

# проверка select_related('owner')
@pytest.mark.django_db
def test_select_related_owner():
    from django.test.utils import CaptureQueriesContext
    from django.db import connection

    user = User.objects.create_user(username='user', password='123')
    Album.objects.create(title='Album 1', owner=user)

    with CaptureQueriesContext(connection) as queries:
        result = list(view_albums(user))
        for album in result:
            _ = album.owner.username  # обращаемся к owner

    # Проверяем, что не было дополнительного запроса для owner
    assert len(queries) == 1

