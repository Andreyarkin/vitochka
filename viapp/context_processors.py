from .services import view_albums


def albums_list(request):
    return {'albums': view_albums(request.user)[:10]}