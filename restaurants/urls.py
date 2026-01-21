from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, DishViewSet, CartItemViewSet,  OrderViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'dishes', DishViewSet)
router.register(r'cart', CartItemViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]
