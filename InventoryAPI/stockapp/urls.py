from django.urls import path
from.views import registration,home,dashboard, logout_success
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    InventoryItemListView,
    InventoryItemCreateView,
    InventoryItemUpdateView,
    InventoryItemDeleteView,
    InventoryLevelsView,
    InventoryActionView,
    RestockItemView,
    SellItemView,
    InventoryChangeLogByNameTemplateView,
    ChangelogsCheckView
)
from .views import InventoryChangeLogView
# , UserDeleteView,UserUpdateView, UserListView

urlpatterns = [
    # path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_edit"),
    # path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    # path("users/", UserListView.as_view(), name="user_list"),
    
    path('register/',registration, name='register'),
    path('',home, name='home'),
    path('login/',LoginView.as_view(template_name = 'registration/login.html'), name= 'login'),
    path('logout/',logout_success, name='logout'),
    path('dashboard/',dashboard, name='dashboard'),
    path('create/', InventoryItemCreateView.as_view(), name='item_create'),
    path('items/', InventoryItemListView.as_view(), name='item_list'),
    path('<int:pk>/update/', InventoryItemUpdateView.as_view(), name='item_update'),
    path('<int:pk>/delete/', InventoryItemDeleteView.as_view(), name='item_delete'),
    
    path('inventory-levels/', InventoryLevelsView.as_view(), name='inventory-levels'),
   
    path("inventory/change-logs-by-name/", InventoryChangeLogByNameTemplateView.as_view(), name="inventory_change_logs_by_name"),


    
    path('inventory/restock/', RestockItemView.as_view(), name='restock-item'),
    path('inventory/sell/', SellItemView.as_view(), name='sell-item'),
    
    
    path('inventory/action/', InventoryActionView.as_view(), name='inventory-action'),
    path('check_logs/',ChangelogsCheckView.as_view(), name='logsredirect')
    
]

