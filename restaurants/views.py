from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, permissions
from .models import Restaurant, Dish, CartItem, Order , OrderItem
from .serializers import RestaurantSerializer, DishSerializer, CartItemSerializer, OrderSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Возвращаем только корзину текущего пользователя
        return CartItem.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Добавление одного или нескольких блюд в корзину.
        Ожидаем список объектов: [{"dish": 1, "quantity": 2}, {"dish": 2, "quantity": 1}]
        """
        items = request.data
        if not isinstance(items, list):
            items = [items]  # если пришёл один объект, оборачиваем в список

        added_items = []

        with transaction.atomic():
            for item in items:
                dish_id = item.get("dish")
                quantity = item.get("quantity", 1)
                
                if not dish_id:
                    continue  # пропускаем некорректные записи
                
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    dish_id=dish_id,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
                
                added_items.append(cart_item)

        serializer = self.get_serializer(added_items, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        cart_item_ids = request.data.get("cart_item_ids", [])
        cart_items = CartItem.objects.filter(id__in=cart_item_ids, user=request.user)

        if not cart_items.exists():
            return Response({"detail": "No valid cart items found"},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            total_price = sum(item.dish.price * item.quantity for item in cart_items)
            order = Order.objects.create(user=request.user, total_price=total_price)

            # Создаём позиции заказа
            for ci in cart_items:
                OrderItem.objects.create(
                    order=order,
                    dish=ci.dish,
                    quantity=ci.quantity
                )

            # Очищаем корзину
            cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ==========================
    #   PUT /api/orders/<id>/status/
    # ==========================
    @action(detail=True, methods=['put'], url_path='status')
    def update_status(self, request, pk=None):
        order = self.get_object()

        # Проверка прав — только владелец или админ
        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You don't have permission to modify this order."},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        valid_statuses = dict(Order.STATUS_CHOICES)

        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Недопустимый статус. Возможные значения: {list(valid_statuses.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        return Response(
            {"id": order.id, "status": order.status},
            status=status.HTTP_200_OK
        )