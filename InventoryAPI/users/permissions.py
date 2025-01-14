
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission class that allows a user to update/delete their own account.
    """
    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed to any user (non-editable data)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Check if the user is trying to modify their own account
        return obj == request.user

