from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)
text_40_validator = RegexValidator(
    regex=r'^[A-Za-zА-Яа-яЁё\s]{1,40}$',
    message='Допустимы только русские и английские буквы, максимум 40 символов'
)

class Restaurant(models.Model):
    name = models.CharField(
        max_length=40,
        validators=[text_40_validator],
        unique=True
    )
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="dishes"
    )

    name = models.CharField(
        max_length=40,
        validators=[text_40_validator]
    )

    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100_000)
        ]
    )

    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('restaurant', 'name')

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"
    

class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ]
    )

    class Meta:
        unique_together = ('user', 'dish')

    def __str__(self):
        return f"{self.quantity} x {self.dish.name} ({self.user.username})"

class Order(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидание'),
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_COMPLETED, 'Выполнен'),
        (STATUS_CANCELLED, 'Отменён'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    cart_items = models.ManyToManyField(
        CartItem,
        related_name="orders"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1_000_000)
        ]
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.user.username})"
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ]
    )

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"
