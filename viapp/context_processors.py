from .models import Album

def albums_list(request):
    return {'albums': Album.objects.all()}