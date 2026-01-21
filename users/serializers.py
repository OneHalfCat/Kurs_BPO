from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers

username_validator = RegexValidator(
    regex=r'^[a-zA-Z][a-zA-Z0-9_]{2,29}$',
    message=(
        "Имя пользователя должно:\n"
        "- начинаться с буквы\n"
        "- содержать только латинские буквы, цифры и _\n"
        "- быть длиной от 3 до 30 символов"
    )
)
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    username = serializers.CharField(
        validators=[username_validator],
        min_length=3,
        max_length=30
    )

    email = serializers.EmailField(
        max_length=254
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
    def validate_username(self, value):
        value = value.lower()

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует."
            )
        return value
    def validate_email(self, value):
        value = value.lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, data):
        if data['username'] in data['password']:
            raise serializers.ValidationError(
                "Пароль не должен содержать имя пользователя."
            )
        return data
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name'
        )
        read_only_fields = ('id', 'username', 'email')
