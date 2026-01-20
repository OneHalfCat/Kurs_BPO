from django.contrib.auth.models import User
from rest_framework import serializers

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) #Пароль ни как не ограничивается, нет минимального размера, нету проверки сложности

    class Meta:
        model = User
        fields = ('username', 'email', 'password') #Почта ни как не проверяется, нету указания обязательности (по умолчанию почта не обязательна)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ('id', 'username', 'email', 'first_name', 'last_name')

