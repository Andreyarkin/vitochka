from rest_framework.permissions import BasePermission

class IsOwnerOrSharedOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser or
            obj.owner == request.user or
            request.user in obj.shared_with.all()
        )