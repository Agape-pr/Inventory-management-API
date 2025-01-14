from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import InventoryItem, InventoryChangeLog
from .serializers import (
    InventoryItemSerializer,
    RestockSellSerializer,
    InventoryChangeLogSerializer,
)





# This view is responsible for two things:
# 1. Displaying all inventory items that belong to the currently logged-in user.
# 2. Allowing the user to add a new inventory item.
class InventoryItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]  # Only logged-in users can access this.

    def get_queryset(self):
        # We only want to show items that belong to the person currently logged in.
        return InventoryItem.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # When creating a new item, we make sure it gets assigned to the current user.
        serializer.save(owner=self.request.user)


# This view handles all the details about a single inventory item.
# Users can:
# - Fetch details of an item.
# - Update an item's details (e.g., name or quantity).
# - Delete an item when it’s no longer needed.
class InventoryItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]  # Only logged-in users can access this.

    def get_queryset(self):
        # Like before, we ensure only the logged-in user's items are shown.
        return InventoryItem.objects.filter(owner=self.request.user)



#views for handling filters

class InventoryLevelView(generics.ListAPIView):
    """
    Endpoint for viewing the current inventory levels with optional filters.
    """
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]  # Only accessible to logged-in users
    
    def get_queryset(self):
        """
        Optionally filter inventory items based on category, price range, or low stock.
        """
        queryset = InventoryItem.objects.all()
        
        # Filtering by category if the `category` query parameter is provided
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Filtering by price range if the `price_min` and/or `price_max` are provided
        price_min = self.request.query_params.get('price_min', None)
        price_max = self.request.query_params.get('price_max', None)
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Filtering for low stock items (e.g., items with quantity less than threshold)
        low_stock = self.request.query_params.get('low_stock', None)
        if low_stock is not None:
            low_stock_threshold = 10  # You can adjust this value based on business needs
            queryset = queryset.filter(quantity__lt=low_stock_threshold)

        return queryset
    
    
    
    # This view handles two actions: restocking (adding quantity) and selling (subtracting quantity).
# The specific action depends on what’s sent in the URL: "restock" or "sell".
class RestockSellItemAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in before doing anything.

    def post(self, request, action_type):
        """
        Handle restocking or selling items based on 'action_type'.
        """
        # Validate the data sent by the user.
        serializer = RestockSellSerializer(data=request.data)
        if serializer.is_valid():
            # Fetch the item the user wants to restock or sell using the name, ensuring it belongs to them.
            item = get_object_or_404(
                InventoryItem, name=serializer.validated_data['name'], owner=request.user
            )
            quantity = serializer.validated_data['quantity']

            # Decide whether we're restocking or selling.
            if action_type == "restock":
                item.quantity += quantity
                action = "restock"
            elif action_type == "sell":
                # Check if there's enough stock to sell the requested quantity.
                if quantity > item.quantity:
                    return Response(
                        {"error": "Not enough stock available."}, status=status.HTTP_400_BAD_REQUEST
                    )
                item.quantity -= quantity
                action = "sale"
            else:
                # If the action type is invalid, inform the user.
                return Response(
                    {"error": "Invalid action type."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Save the updated quantity and log what happened.
            item.save()
            InventoryChangeLog.objects.create(
                inventory_item=item,
                action=action,
                change_quantity=quantity if action == "restock" else -quantity,
                user=request.user
            )

            # Let the user know everything worked.
            return Response(
                {"success": f"Item '{item.name}' {action}ed successfully."}, status=status.HTTP_200_OK
            )

        # If something goes wrong, return an error with details.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# This view retrieves the history of changes (logs) for a specific inventory item.
class InventoryChangeLogAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only accessible to logged-in users.

    def get(self, request):
        """
        Fetch the change log for an inventory item by its name.
        """
        # Get the product name from the request.
        product_name = request.query_params.get("product_name", "").strip()

        # Check if the user provided a valid product name.
        if not product_name:
            return Response({"error": "Please provide a product name."}, status=status.HTTP_400_BAD_REQUEST)

        # Try to find the inventory item by name, ensuring it belongs to the current user.
        product = get_object_or_404(InventoryItem, name__iexact=product_name, owner=request.user)

        # Fetch all the logs associated with this item, sorted by the latest change.
        change_logs = InventoryChangeLog.objects.filter(inventory_item=product).order_by("-created_at")

        # Convert the logs into a format that can be sent back in the response.
        serializer = InventoryChangeLogSerializer(change_logs, many=True)

        # Send the logs back to the user.
        return Response(
            {"product": product.name, "change_logs": serializer.data}, status=status.HTTP_200_OK
        )
