from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json


class UserModelTest(TestCase):
    """Unit-тесты для модели User"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_create_user_without_email(self):
        """Тест создания пользователя без email"""
        user_data = self.user_data.copy()
        del user_data['email']
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.email, '')
    
    def test_user_string_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')


class UserRegistrationTest(APITestCase):
    """Unit-тесты для регистрации пользователей"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.valid_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
    
    def test_register_valid_user(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Проверяем, что пароль захеширован
        user = User.objects.get(username='newuser')
        self.assertNotEqual(user.password, 'newpass123')
        self.assertTrue(user.check_password('newpass123'))
    
    def test_register_duplicate_username(self):
        """Тест регистрации с существующим username"""
        User.objects.create_user(**self.valid_user_data)
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_duplicate_email(self):
        """Тест регистрации с существующим email"""
        User.objects.create_user(**self.valid_user_data)
        new_data = self.valid_user_data.copy()
        new_data['username'] = 'anotheruser'
        response = self.client.post(self.register_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_invalid_data(self):
        """Тест регистрации с невалидными данными"""
        invalid_data = {
            'username': '',
            'email': 'invalid-email',
            'password': ''
        }
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_missing_fields(self):
        """Тест регистрации с отсутствующими полями"""
        incomplete_data = {'username': 'testuser'}
        response = self.client.post(self.register_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthenticationTest(APITestCase):
    """Unit-тесты для аутентификации пользователей"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_login_valid_credentials(self):
        """Тест входа с корректными учетными данными"""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_username(self):
        """Тест входа с неверным username"""
        login_data = {
            'username': 'wronguser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_invalid_password(self):
        """Тест входа с неверным паролем"""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_missing_credentials(self):
        """Тест входа без учетных данных"""
        response = self.client.post(self.login_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTest(APITestCase):
    """Unit-тесты для профиля пользователя"""
    
    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('profile')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        # Получаем JWT токен для аутентификации
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    def test_get_profile_authenticated(self):
        """Тест получения профиля аутентифицированным пользователем"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
    
    def test_get_profile_unauthenticated(self):
        """Тест получения профиля неаутентифицированным пользователем"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    
    def test_update_profile_unauthenticated(self):
        """Тест обновления профиля неаутентифицированным пользователем"""
        update_data = {'first_name': 'Updated'}
        response = self.client.patch(self.profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserIntegrationTest(APITestCase):
    """Интеграционные тесты для полного цикла работы с пользователями"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
    
    def test_full_user_lifecycle(self):
        """Тест полного жизненного цикла пользователя: регистрация -> вход -> работа с профилем"""
        # 1. Регистрация
        register_data = {
            'username': 'lifecycle_user',
            'email': 'lifecycle@example.com',
            'password': 'lifecycle123'
        }
        register_response = self.client.post(self.register_url, register_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # 2. Вход в систему
        login_data = {
            'username': 'lifecycle_user',
            'password': 'lifecycle123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data['access']
        
        # 3. Получение профиля
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['username'], 'lifecycle_user')
        
        # 4. Обновление профиля
        update_data = {
            'first_name': 'Lifecycle',
            'last_name': 'Test'
        }
        update_response = self.client.patch(self.profile_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # 5. Проверка обновленных данных
        final_profile_response = self.client.get(self.profile_url)
        self.assertEqual(final_profile_response.data['first_name'], 'Lifecycle')
        self.assertEqual(final_profile_response.data['last_name'], 'Test')
    
    def test_token_refresh_flow(self):
        """Тест обновления JWT токенов"""
        # Создаем пользователя и получаем токены
        user = User.objects.create_user(
            username='refresh_user',
            password='refresh123'
        )
        login_data = {
            'username': 'refresh_user',
            'password': 'refresh123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Обновляем токен
        refresh_url = reverse('token_refresh')
        refresh_response = self.client.post(refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
        
        # Используем новый токен для доступа к профилю
        new_access_token = refresh_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
