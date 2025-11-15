from rest_framework import serializers
from .models import Restaurant, Dish, CartItem, Order


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'

class DishInfoSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Dish
        fields = ['id', 'name', 'restaurant_name', 'price']

class CartItemSerializer(serializers.ModelSerializer):
    # Для чтения используем вложенный сериализатор
    dish_info = DishInfoSerializer(source='dish', read_only=True)
    # Для записи оставляем ID
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.all(), write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'quantity', 'dish', 'dish_info']

class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'status', 'created_at']
        read_only_fields = ['user', 'total_price', 'status', 'created_at']