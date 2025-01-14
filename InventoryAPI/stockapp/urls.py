from django.urls import path
from .views import (
    InventoryItemListCreateAPIView,
    InventoryItemRetrieveUpdateDestroyAPIView,
    RestockSellItemAPIView,
    InventoryChangeLogAPIView,
)
from .views import InventoryLevelView
urlpatterns = [
    # Endpoint for listing and creating inventory items.
    path('inventory/', InventoryItemListCreateAPIView.as_view(), name='inventory-list-create'),

    # Endpoint for retrieving, updating, and deleting a specific inventory item by ID.
    path('inventory/<int:pk>/', InventoryItemRetrieveUpdateDestroyAPIView.as_view(), name='inventory-detail'),

    # Endpoint for restocking an inventory item.
    path('inventory/restock/', RestockSellItemAPIView.as_view(), {'action_type': 'restock'}, name='inventory-restock'),

    # Endpoint for selling an inventory item.
    path('inventory/sell/', RestockSellItemAPIView.as_view(), {'action_type': 'sell'}, name='inventory-sell'),

    # Endpoint for fetching change logs for an item by its name.
    path('inventory/logs/', InventoryChangeLogAPIView.as_view(), name='inventory-logs'),
    path('inventory/levels/', InventoryLevelView.as_view(), name='inventory-levels')
]
