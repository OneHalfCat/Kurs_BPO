from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from .models import Restaurant, Dish, CartItem, Order, OrderItem


class RestaurantModelTest(TestCase):
    """Unit-тесты для модели Restaurant"""
    
    def setUp(self):
        self.restaurant_data = {
            'name': 'Test Restaurant',
            'address': '123 Test Street',
            'description': 'A test restaurant'
        }
    
    def test_create_restaurant(self):
        """Тест создания ресторана"""
        restaurant = Restaurant.objects.create(**self.restaurant_data)
        self.assertEqual(restaurant.name, 'Test Restaurant')
        self.assertEqual(restaurant.address, '123 Test Street')
        self.assertEqual(restaurant.description, 'A test restaurant')
    
    def test_restaurant_string_representation(self):
        """Тест строкового представления ресторана"""
        restaurant = Restaurant.objects.create(**self.restaurant_data)
        self.assertEqual(str(restaurant), 'Test Restaurant')


class DishModelTest(TestCase):
    """Unit-тесты для модели Dish"""
    
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='123 Test Street'
        )
        self.dish_data = {
            'restaurant': self.restaurant,
            'name': 'Test Dish',
            'description': 'A delicious test dish',
            'price': Decimal('15.99'),
            'is_available': True
        }
    
    def test_create_dish(self):
        """Тест создания блюда"""
        dish = Dish.objects.create(**self.dish_data)
        self.assertEqual(dish.name, 'Test Dish')
        self.assertEqual(dish.restaurant, self.restaurant)
        self.assertEqual(dish.price, Decimal('15.99'))
        self.assertTrue(dish.is_available)
    
    def test_dish_string_representation(self):
        """Тест строкового представления блюда"""
        dish = Dish.objects.create(**self.dish_data)
        expected_str = f"Test Dish (Test Restaurant)"
        self.assertEqual(str(dish), expected_str)
    
    def test_dish_price_validation(self):
        """Тест валидации цены блюда (должна быть положительной)"""
        dish_data = self.dish_data.copy()
        dish_data['price'] = Decimal('-5.00')
        dish = Dish(**dish_data)
        
        # Проверяем, что валидация не пройдет
        with self.assertRaises(Exception):
            dish.full_clean()


class CartItemModelTest(TestCase):
    """Unit-тесты для модели CartItem"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='123 Test Street'
        )
        self.dish = Dish.objects.create(
            restaurant=self.restaurant,
            name='Test Dish',
            price=Decimal('10.00')
        )
    
    def test_create_cart_item(self):
        """Тест создания элемента корзины"""
        cart_item = CartItem.objects.create(
            user=self.user,
            dish=self.dish,
            quantity=2
        )
        self.assertEqual(cart_item.user, self.user)
        self.assertEqual(cart_item.dish, self.dish)
        self.assertEqual(cart_item.quantity, 2)
    
    def test_cart_item_string_representation(self):
        """Тест строкового представления элемента корзины"""
        cart_item = CartItem.objects.create(
            user=self.user,
            dish=self.dish,
            quantity=3
        )
        expected_str = f"3 x Test Dish (testuser)"
        self.assertEqual(str(cart_item), expected_str)


class OrderModelTest(TestCase):
    """Unit-тесты для модели Order"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='123 Test Street'
        )
        self.dish = Dish.objects.create(
            restaurant=self.restaurant,
            name='Test Dish',
            price=Decimal('15.00')
        )
    
    def test_create_order(self):
        """Тест создания заказа"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('30.00'),
            status='PENDING'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, Decimal('30.00'))
        self.assertEqual(order.status, 'PENDING')
    
    def test_order_string_representation(self):
        """Тест строкового представления заказа"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('25.00')
        )
        expected_str = f"Order #{order.id} (testuser)"
        self.assertEqual(str(order), expected_str)
    
    def test_order_default_status(self):
        """Тест статуса заказа по умолчанию"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('20.00')
        )
        self.assertEqual(order.status, 'PENDING')


class RestaurantAPITest(APITestCase):
    """Unit-тесты для API ресторанов"""
    
    def setUp(self):
        self.client = APIClient()
        self.restaurant_data = {
            'name': 'API Test Restaurant',
            'address': '456 API Street',
            'description': 'Restaurant for API testing'
        }
    
    def test_get_restaurants_list(self):
        """Тест получения списка ресторанов"""
        Restaurant.objects.create(**self.restaurant_data)
        url = '/api/restaurants/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'API Test Restaurant')
    
    def test_get_restaurant_detail(self):
        """Тест получения детальной информации о ресторане"""
        restaurant = Restaurant.objects.create(**self.restaurant_data)
        url = f'/api/restaurants/{restaurant.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'API Test Restaurant')
    
    def test_create_restaurant(self):
        """Тест создания ресторана через API"""
        url = '/api/restaurants/'
        response = self.client.post(url, self.restaurant_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Restaurant.objects.filter(name='API Test Restaurant').exists())


class DishAPITest(APITestCase):
    """Unit-тесты для API блюд"""
    
    def setUp(self):
        self.client = APIClient()
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='123 Test Street'
        )
        self.dish_data = {
            'restaurant': self.restaurant.id,
            'name': 'API Test Dish',
            'description': 'Dish for API testing',
            'price': '12.99',
            'is_available': True
        }
    
    def test_get_dishes_list(self):
        """Тест получения списка блюд"""
        Dish.objects.create(
            restaurant=self.restaurant,
            name='Test Dish',
            price=Decimal('10.00')
        )
        url = '/api/dishes/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_dish(self):
        """Тест создания блюда через API"""
        url = '/api/dishes/'
        response = self.client.post(url, self.dish_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Dish.objects.filter(name='API Test Dish').exists())


class CartAPITest(APITestCase):
    """Unit-тесты для API корзины"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='cartuser',
            password='cartpass123'
        )
        self.restaurant = Restaurant.objects.create(
            name='Cart Restaurant',
            address='789 Cart Street'
        )
        self.dish = Dish.objects.create(
            restaurant=self.restaurant,
            name='Cart Dish',
            price=Decimal('8.50')
        )
        
        # Аутентификация пользователя
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_add_item_to_cart(self):
        """Тест добавления элемента в корзину"""
        url = '/api/cart/'
        cart_data = {
            'dish': self.dish.id,
            'quantity': 2
        }
        response = self.client.post(url, cart_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CartItem.objects.filter(user=self.user, dish=self.dish).exists())
    
    def test_get_cart_items(self):
        """Тест получения элементов корзины"""
        CartItem.objects.create(
            user=self.user,
            dish=self.dish,
            quantity=1
        )
        url = '/api/cart/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_add_multiple_items_to_cart(self):
        """Тест добавления нескольких элементов в корзину"""
        dish2 = Dish.objects.create(
            restaurant=self.restaurant,
            name='Second Dish',
            price=Decimal('12.00')
        )
        
        url = '/api/cart/'
        cart_data = [
            {'dish': self.dish.id, 'quantity': 2},
            {'dish': dish2.id, 'quantity': 1}
        ]
        response = self.client.post(url, cart_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 2)
    
    def test_cart_access_unauthenticated(self):
        """Тест доступа к корзине неаутентифицированным пользователем"""
        self.client.credentials()  # Убираем аутентификацию
        url = '/api/cart/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderAPITest(APITestCase):
    """Unit-тесты для API заказов"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='orderuser',
            password='orderpass123'
        )
        self.restaurant = Restaurant.objects.create(
            name='Order Restaurant',
            address='321 Order Street'
        )
        self.dish = Dish.objects.create(
            restaurant=self.restaurant,
            name='Order Dish',
            price=Decimal('15.00')
        )
        self.cart_item = CartItem.objects.create(
            user=self.user,
            dish=self.dish,
            quantity=2
        )
        
        # Аутентификация пользователя
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_create_order_from_cart(self):
        """Тест создания заказа из корзины"""
        url = '/api/orders/'
        order_data = {
            'cart_item_ids': [self.cart_item.id]
        }
        response = self.client.post(url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что заказ создался
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_price, Decimal('30.00'))  # 15.00 * 2
        
        # Проверяем, что корзина очистилась
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
    
    def test_get_user_orders(self):
        """Тест получения заказов пользователя"""
        Order.objects.create(
            user=self.user,
            total_price=Decimal('25.00')
        )
        url = '/api/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_update_order_status(self):
        """Тест обновления статуса заказа"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('20.00'),
            status='PENDING'
        )
        url = f'/api/orders/{order.id}/status/'
        status_data = {'status': 'IN_PROGRESS'}
        response = self.client.put(url, status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что статус обновился
        order.refresh_from_db()
        self.assertEqual(order.status, 'IN_PROGRESS')
    
    def test_update_order_status_invalid(self):
        """Тест обновления статуса заказа на недопустимый"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('20.00')
        )
        url = f'/api/orders/{order.id}/status/'
        status_data = {'status': 'INVALID_STATUS'}
        response = self.client.put(url, status_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_order_empty_cart(self):
        """Тест создания заказа с пустой корзиной"""
        url = '/api/orders/'
        order_data = {'cart_item_ids': []}
        response = self.client.post(url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RestaurantIntegrationTest(APITestCase):
    """Интеграционные тесты для полного цикла работы с рестораном"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='integration_user',
            password='integration123'
        )
        
        # Аутентификация пользователя
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_full_order_lifecycle(self):
        """Тест полного жизненного цикла заказа: ресторан -> блюдо -> корзина -> заказ"""
        
        # 1. Создаем ресторан
        restaurant_data = {
            'name': 'Integration Restaurant',
            'address': '999 Integration Ave',
            'description': 'Full cycle test restaurant'
        }
        restaurant_response = self.client.post('/api/restaurants/', restaurant_data, format='json')
        self.assertEqual(restaurant_response.status_code, status.HTTP_201_CREATED)
        restaurant_id = restaurant_response.data['id']
        
        # 2. Создаем блюдо
        dish_data = {
            'restaurant': restaurant_id,
            'name': 'Integration Dish',
            'description': 'Test dish for integration',
            'price': '18.50',
            'is_available': True
        }
        dish_response = self.client.post('/api/dishes/', dish_data, format='json')
        self.assertEqual(dish_response.status_code, status.HTTP_201_CREATED)
        dish_id = dish_response.data['id']
        
        # 3. Добавляем блюдо в корзину
        cart_data = {
            'dish': dish_id,
            'quantity': 3
        }
        cart_response = self.client.post('/api/cart/', cart_data, format='json')
        self.assertEqual(cart_response.status_code, status.HTTP_201_CREATED)
        
        # 4. Проверяем корзину
        cart_list_response = self.client.get('/api/cart/')
        self.assertEqual(len(cart_list_response.data), 1)
        cart_item_id = cart_list_response.data[0]['id']
        
        # 5. Создаем заказ из корзины
        order_data = {
            'cart_item_ids': [cart_item_id]
        }
        order_response = self.client.post('/api/orders/', order_data, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        order_id = order_response.data['id']
        
        # 6. Проверяем, что заказ создался с правильной суммой
        expected_total = Decimal('18.50') * 3  # 55.50
        self.assertEqual(Decimal(order_response.data['total_price']), expected_total)
        
        # 7. Обновляем статус заказа
        status_update_response = self.client.put(
            f'/api/orders/{order_id}/status/',
            {'status': 'COMPLETED'},
            format='json'
        )
        self.assertEqual(status_update_response.status_code, status.HTTP_200_OK)
        
        # 8. Проверяем финальный статус
        final_order_response = self.client.get('/api/orders/')
        self.assertEqual(final_order_response.data[0]['status'], 'COMPLETED')
        
        # 9. Проверяем, что корзина очистилась
        final_cart_response = self.client.get('/api/cart/')
        self.assertEqual(len(final_cart_response.data), 0)
    
    def test_multiple_restaurants_and_dishes(self):
        """Тест работы с несколькими ресторанами и блюдами"""
        
        # Создаем два ресторана
        restaurant1 = Restaurant.objects.create(
            name='Restaurant One',
            address='111 First St'
        )
        restaurant2 = Restaurant.objects.create(
            name='Restaurant Two',
            address='222 Second St'
        )
        
        # Создаем блюда в каждом ресторане
        dish1 = Dish.objects.create(
            restaurant=restaurant1,
            name='Dish from Restaurant 1',
            price=Decimal('10.00')
        )
        dish2 = Dish.objects.create(
            restaurant=restaurant2,
            name='Dish from Restaurant 2',
            price=Decimal('15.00')
        )
        
        # Добавляем оба блюда в корзину
        cart_data = [
            {'dish': dish1.id, 'quantity': 2},
            {'dish': dish2.id, 'quantity': 1}
        ]
        cart_response = self.client.post('/api/cart/', cart_data, format='json')
        self.assertEqual(cart_response.status_code, status.HTTP_201_CREATED)
        
        # Получаем корзину и создаем заказ
        cart_list_response = self.client.get('/api/cart/')
        cart_item_ids = [item['id'] for item in cart_list_response.data]
        
        order_data = {'cart_item_ids': cart_item_ids}
        order_response = self.client.post('/api/orders/', order_data, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем общую сумму заказа (10*2 + 15*1 = 35)
        expected_total = Decimal('35.00')
        self.assertEqual(Decimal(order_response.data['total_price']), expected_total)
