from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import AlbumSerializer
from .permissions import IsOwnerOrSharedOrAdmin
from .services import view_albums, view_and_download, can_create_album, edit_content

class AlbumListView(generics.ListCreateAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return view_albums(self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class AlbumDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSharedOrAdmin]

    def get_queryset(self):
        return view_albums(self.request.user)
