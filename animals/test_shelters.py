
import pytest

from animals.models import Shelter


pytestmark = pytest.mark.django_db

SHELTERS_URL = "/api/shelters"


def valid_shelter_data():
    return {
        "name": "Новий притулок",
        "city": "Львів",
        "address": "Вулиця Шевченка, 10",
        "phone": "+380671234567",
        "description": "Тестовий опис",
    }


# GET — перегляд притулків


def test_guest_can_view_shelters(api_client, shelter):
    response = api_client.get(SHELTERS_URL)

    assert response.status_code == 200
    assert len(response.data["shelters"]) == 1
    assert response.data["shelters"][0]["id"] == shelter.id


def test_guest_can_view_shelter_detail(api_client, shelter):
    response = api_client.get(f"{SHELTERS_URL}/{shelter.id}")

    assert response.status_code == 200
    assert response.data["name"] == shelter.name


def test_filter_shelters_by_city(api_client, shelter):
    response = api_client.get(
        SHELTERS_URL,
        {"city": "Київ"},
    )

    assert response.status_code == 200
    assert len(response.data["shelters"]) == 1


# POST — створення притулків


def test_authenticated_user_can_create_shelter(auth_client):
    response = auth_client.post(
        SHELTERS_URL,
        valid_shelter_data(),
        format="json",
    )

    assert response.status_code == 201
    assert Shelter.objects.count() == 1


def test_guest_cannot_create_shelter(api_client):
    response = api_client.post(
        SHELTERS_URL,
        valid_shelter_data(),
        format="json",
    )

    assert response.status_code == 401
    assert Shelter.objects.count() == 0


def test_cannot_create_shelter_with_invalid_data(auth_client):
    data = valid_shelter_data()
    data["name"] = ""

    response = auth_client.post(
        SHELTERS_URL,
        data,
        format="json",
    )

    assert response.status_code == 400
    assert "name" in response.data["details"]


# PATCH — редагування притулків


def test_authenticated_user_can_edit_shelter(auth_client, shelter):
    response = auth_client.patch(
        f"{SHELTERS_URL}/{shelter.id}",
        {"city": "Одеса"},
        format="json",
    )

    assert response.status_code == 200

    shelter.refresh_from_db()
    assert shelter.city == "Одеса"


def test_guest_cannot_edit_shelter(api_client, shelter):
    response = api_client.patch(
        f"{SHELTERS_URL}/{shelter.id}",
        {"city": "Одеса"},
        format="json",
    )

    assert response.status_code == 401

    shelter.refresh_from_db()
    assert shelter.city == "Київ"


def test_invalid_shelter_update(auth_client, shelter):
    response = auth_client.patch(
        f"{SHELTERS_URL}/{shelter.id}",
        {"name": ""},
        format="json",
    )

    assert response.status_code == 400


# DELETE — видалення притулків


def test_regular_user_cannot_delete_shelter(auth_client, shelter):
    response = auth_client.delete(
        f"{SHELTERS_URL}/{shelter.id}"
    )

    assert response.status_code == 403
    assert Shelter.objects.filter(id=shelter.id).exists()


def test_guest_cannot_delete_shelter(api_client, shelter):
    response = api_client.delete(
        f"{SHELTERS_URL}/{shelter.id}"
    )

    assert response.status_code == 401
    assert Shelter.objects.filter(id=shelter.id).exists()


def test_admin_can_delete_empty_shelter(admin_client, shelter):
    response = admin_client.delete(
        f"{SHELTERS_URL}/{shelter.id}"
    )

    assert response.status_code == 204
    assert not Shelter.objects.filter(id=shelter.id).exists()


def test_cannot_delete_nonexistent_shelter(admin_client):
    response = admin_client.delete(
        f"{SHELTERS_URL}/999999"
    )

    assert response.status_code == 404


def test_cannot_delete_shelter_with_animals(admin_client, animal):
    shelter_id = animal.shelter_id

    response = admin_client.delete(
        f"{SHELTERS_URL}/{shelter_id}"
    )

    assert response.status_code == 409
    assert Shelter.objects.filter(id=shelter_id).exists()


# GET — неіснуючий притулок


def test_nonexistent_shelter_returns_404(api_client):
    response = api_client.get(
        f"{SHELTERS_URL}/999999"
    )

    assert response.status_code == 404
