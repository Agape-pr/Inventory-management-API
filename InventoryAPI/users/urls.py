# users/urls.py
from django.urls import path
from .views import UserListView, UserDetailView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),  # List or create users
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),  # Update or delete specific users
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]






