from django.urls import path

from .views import (
    AnimalDetailAPIView,
    AnimalListAPIView,
    ShelterAnimalsAPIView,
    ShelterDetailAPIView,
    ShelterListAPIView,
)

urlpatterns = [
    path("animals", AnimalListAPIView.as_view(), name="animal-list"),
    path(
        "animals/<int:pk>",
        AnimalDetailAPIView.as_view(),
        name="animal-detail",
    ),
    path("shelters", ShelterListAPIView.as_view(), name="shelter-list"),
    path(
        "shelters/<int:pk>",
        ShelterDetailAPIView.as_view(),
        name="shelter-detail",
    ),
    path(
        "shelters/<int:pk>/animals",
        ShelterAnimalsAPIView.as_view(),
        name="shelter-animals",
    ),
]
