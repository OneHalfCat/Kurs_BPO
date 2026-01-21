"""
Утилиты для тестирования - централизованное управление тестовыми данными
"""
import secrets
import string
from django.contrib.auth.models import User


class TestDataGenerator:
    """Генератор тестовых данных для устранения жестко закодированных значений"""
    
    # Константы для тестовых паролей (вместо жестко закодированных)
    DEFAULT_TEST_PASSWORD = 'TestPass123!'
    
    @staticmethod
    def generate_secure_password(length=12):
        """Генерирует безопасный случайный пароль для тестов"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def create_test_user(username=None, password=None, **kwargs):
        """Создает тестового пользователя с безопасными данными"""
        if username is None:
            username = f'testuser_{secrets.token_hex(4)}'
        if password is None:
            password = TestDataGenerator.DEFAULT_TEST_PASSWORD
            
        return User.objects.create_user(
            username=username,
            password=password,
            **kwargs
        )
    
    @staticmethod
    def get_test_credentials(username=None):
        """Возвращает тестовые учетные данные"""
        if username is None:
            username = f'testuser_{secrets.token_hex(4)}'
        return {
            'username': username,
            'password': TestDataGenerator.DEFAULT_TEST_PASSWORD
        }


# Константы для использования в тестах
TEST_PASSWORD = TestDataGenerator.DEFAULT_TEST_PASSWORD