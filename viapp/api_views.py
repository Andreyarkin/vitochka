from rest_framework import generics
from .models import Album
from .serializers import AlbumSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrSharedOrAdmin
from django.db.models import Q

class AlbumListView(generics.ListCreateAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Album.objects.all()

        return Album.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class AlbumDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSharedOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Album.objects.all()

        return Album.objects.filter(
            Q(owner=user) | Q(shared_with=user)
        ).distinct()