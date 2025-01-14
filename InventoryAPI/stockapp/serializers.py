from rest_framework import serializers
from .models import InventoryItem, InventoryChangeLog
from rest_framework import serializers  


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        # Define the model and fields to interact with the inventory items.
        model = InventoryItem
        fields = '__all__'  # Inc
        
        

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'description', 'quantity', 'price', 'category', 'date_added', 'owner']
        read_only_fields = ['id', 'date_added', 'owner']



class RestockSellSerializer(serializers.Serializer):
    name = serializers.CharField()  # For item name lookup
    quantity = serializers.IntegerField()


class InventoryChangeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryChangeLog
        fields = ['id', 'action', 'change_quantity', 'created_at']
