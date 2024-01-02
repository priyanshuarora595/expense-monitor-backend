from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.id == view.kwargs.get("pk"))
