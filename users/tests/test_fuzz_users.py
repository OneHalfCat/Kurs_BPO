import pytest
from hypothesis import given, settings, strategies as st
from users.serializers import UserRegisterSerializer

@settings(
    max_examples=100,     # сколько тест-кейсов
    deadline=None,              # отключаем таймаут
    derandomize=False,
)
@given(
    username=st.text(min_size=0, max_size=300),
    email=st.text(min_size=0, max_size=300),
    password=st.text(min_size=0, max_size=300),
)
def test_user_register_fuzz(username, email, password):
    data = {
        "username": username,
        "email": email,
        "password": password,
    }

    serializer = UserRegisterSerializer(data=data)

    try:
        valid = serializer.is_valid()
        if valid:
            user = serializer.save()
            assert user.username
    except Exception as e:
        # ❗ КРИТИЧЕСКОЕ: ловим только неожиданные падения
        assert isinstance(e, (ValidationError, ValueError))
