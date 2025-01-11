from rest_framework import serializers
from .models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'description', 'quantity', 'price', 'category', 'date_added', 'last_updated']
        read_only_fields = ['date_added', 'last_updated']
        
    def validate(self, data):
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        if data['price'] <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return data      
    
    
    
    
from rest_framework import serializers
from .models import InventoryChangeLog

class InventoryChangeLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.email', read_only=True)
    item_name = serializers.CharField(source='inventory_item.name', read_only=True)

    class Meta:
        model = InventoryChangeLog
        fields = [
            "id",
            "item_name",   
            "action",      
            "change_quantity",
            "user_name",   
        ]
 
    
    