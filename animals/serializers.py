from rest_framework import serializers

from .models import Animal, Shelter


class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = [
            "id",
            "name",
            "city",
            "address",
            "phone",
            "description",
        ]
        read_only_fields = ["id"]


class AnimalSerializer(serializers.ModelSerializer):
    shelter_id = serializers.PrimaryKeyRelatedField(
        source="shelter",
        queryset=Shelter.objects.all(),
    )

    class Meta:
        model = Animal
        fields = [
            "id",
            "name",
            "species",
            "breed",
            "age_months",
            "sex",
            "description",
            "photo_url",
            "status",
            "shelter_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
