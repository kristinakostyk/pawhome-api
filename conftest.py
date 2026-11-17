
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from animals.models import Animal, Shelter


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def regular_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="test_user",
        password="StrongPass2026!",
    )


@pytest.fixture
def admin_user(db, django_user_model):
    return django_user_model.objects.create_superuser(
        username="test_admin",
        email="admin@example.com",
        password="StrongPass2026!",
    )


@pytest.fixture
def auth_client(regular_user):
    client = APIClient()
    access = RefreshToken.for_user(regular_user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    access = RefreshToken.for_user(admin_user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


@pytest.fixture
def shelter(db):
    return Shelter.objects.create(
        name="Тестовий притулок",
        city="Київ",
        address="Тестова вулиця, 1",
        phone="+380501234567",
        description="Притулок для тестування",
    )


@pytest.fixture
def animal(shelter):
    return Animal.objects.create(
        shelter=shelter,
        name="Рекс",
        species="dog",
        breed="Метис",
        age_months=12,
        sex="male",
        status="available",
    )
