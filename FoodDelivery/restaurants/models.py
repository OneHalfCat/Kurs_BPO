from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"
    

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # количество, только положительное

    def __str__(self):
        return f"{self.quantity} x {self.dish.name} ({self.user.username})"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Ожидание'),
        ('IN_PROGRESS', 'В процессе'),
        ('COMPLETED', 'Выполнен'),
        ('CANCELLED', 'Отменён'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    cart_items = models.ManyToManyField(CartItem, related_name="orders")  # элементы из корзины
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.user.username})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")  # отдельные позиции заказа
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"