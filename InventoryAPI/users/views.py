# users/views.py
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from django.contrib.auth import get_user_model

from .permissions import IsOwnerOrReadOnly
class UserListView(generics.ListCreateAPIView):
    """
    Endpoint for listing users or creating a new user.
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny] 
    queryset = get_user_model().objects.all()  # or filter based on specific needs
    def perform_create(self, serializer):
        serializer.save()
        
        


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoint for retrieving, updating or deleting a user.
    Only the user himself can update or delete.
    """
    
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # Restrict update or delete to the user owning the account
    def get_object(self):
        return self.request.user
