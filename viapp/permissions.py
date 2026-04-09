from rest_framework.permissions import BasePermission
from .services import view_and_download

class IsOwnerOrSharedOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return view_and_download(request.user, obj)