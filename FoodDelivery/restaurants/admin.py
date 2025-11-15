from django.contrib import admin
from .models import Restaurant, Dish, CartItem, Order

# Регистрируем модели, чтобы видеть их в админке
admin.site.register(Restaurant)
admin.site.register(Dish)
admin.site.register(CartItem)
admin.site.register(Order)
