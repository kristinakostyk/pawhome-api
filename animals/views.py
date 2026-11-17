import logging
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Animal, Shelter
from .serializers import AnimalSerializer, ShelterSerializer
from .permissions import IsAdminForShelterDelete
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    inline_serializer,
)
from rest_framework import serializers
logger = logging.getLogger("animals")

def api_error(message, status_code, details=None):
    return Response(
        {"error": message, "details": details or {}},
        status=status_code,
    )



class ShelterListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        operation_id="shelters_list",
        summary="Get all shelters",
        description="Returns a list of shelters. Authentication is not required.",
        parameters=[
            OpenApiParameter(
                name="city",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter shelters by city.",
            ),
        ],
        responses={
            200: inline_serializer(
                name="ShelterListResponse",
                fields={
                    "shelters": ShelterSerializer(many=True),
                },
            ),
        },
        auth=[],
    )
    def get(self, request):
        shelters = Shelter.objects.all().order_by("id")

        city = request.query_params.get("city")
        if city:
            shelters = shelters.filter(city__icontains=city)

        serializer = ShelterSerializer(shelters, many=True)
        return Response({"shelters": serializer.data})

    @extend_schema(
        operation_id="shelters_create",
        summary="Create a shelter",
        description="Creates a new shelter. Requires JWT authentication.",
        request=ShelterSerializer,
        responses={
            201: ShelterSerializer,
            400: OpenApiResponse(description="Invalid shelter data."),
            401: OpenApiResponse(description="Authentication required."),
        },
        examples=[
            OpenApiExample(
                "Create shelter example",
                value={
                    "name": "Happy Paws",
                    "city": "Kyiv",
                    "address": "Main Street 10",
                    "phone": "+380501234567",
                    "description": "Animal shelter",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid shelter example",
                value={
                    "error": "Некоректні дані притулку.",
                    "details": {
                        "name": ["This field may not be blank."]
                    },
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        serializer = ShelterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            logger.info(
                "Shelter created: id=%s",
                serializer.instance.id
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        logger.warning("Shelter creation failed: invalid input")
        return api_error(
            "Некоректні дані притулку.",
            status.HTTP_400_BAD_REQUEST,
            serializer.errors,
        )


class ShelterDetailAPIView(APIView):
    permission_classes = [
    IsAuthenticatedOrReadOnly,
    IsAdminForShelterDelete,
    ]

    def get_shelter(self, pk):
        return Shelter.objects.filter(pk=pk).first()

    @extend_schema(
        operation_id="shelters_retrieve",
        summary="Get shelter details",
        description="Returns information about a shelter by ID. Public endpoint.",
        responses={
            200: ShelterSerializer,
            404: OpenApiResponse(description="Shelter not found."),
        },
        auth=[],
    )

    def get(self, request, pk):
        shelter = self.get_shelter(pk)
        if shelter is None:
            return api_error(
                "Притулок не знайдено.",
                status.HTTP_404_NOT_FOUND,
            )

        serializer = ShelterSerializer(shelter)
        return Response(serializer.data)


    @extend_schema(
        operation_id="shelters_partial_update",
        summary="Update shelter",
        description="Partially updates shelter information. JWT authentication required.",
        request=ShelterSerializer(partial=True),
        responses={
            200: ShelterSerializer,
            400: OpenApiResponse(description="Invalid shelter data."),
            401: OpenApiResponse(description="Authentication required."),
            404: OpenApiResponse(description="Shelter not found."),
        },
        examples=[
            OpenApiExample(
                "Update shelter city",
                value={"city": "Lviv"},
                request_only=True,
            ),
        ],
    )


    def patch(self, request, pk):
        shelter = self.get_shelter(pk)
        if shelter is None:
            return api_error(
                "Притулок не знайдено.",
                status.HTTP_404_NOT_FOUND,
            )

        serializer = ShelterSerializer(
            shelter,
            data=request.data,
            partial=True,
        )


        if serializer.is_valid():
            serializer.save()
            logger.info(
                "Shelter updated: id=%s",
                shelter.id,
            )
            return Response(serializer.data)

        logger.warning(
            "Shelter update failed: invalid input; id=%s",
            shelter.id,
        )
        return api_error(
            "Некоректні дані притулку.",
            status.HTTP_400_BAD_REQUEST,
            serializer.errors,
        )



    @extend_schema(
        operation_id="shelters_destroy",
        summary="Delete shelter",
        description=(
            "Deletes an empty shelter. "
            "Only administrators with is_staff=True can delete shelters. "
            "Shelters containing animals cannot be deleted."
        ),
        responses={
            204: OpenApiResponse(description="Shelter deleted successfully. No content."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Administrator permissions required."),
            404: OpenApiResponse(description="Shelter not found."),
            409: OpenApiResponse(description="Shelter contains animals and cannot be deleted."),
        },
    )


    def delete(self, request, pk):
        shelter = self.get_shelter(pk)

        if shelter is None:
            logger.warning(
                "Shelter deletion failed: not found; id=%s",
                pk,
            )
            return api_error(
                "Притулок не знайдено.",
                status.HTTP_404_NOT_FOUND,
            )

        animal_count = shelter.animals.count()

        if animal_count > 0:
            logger.warning(
                "Shelter deletion blocked: id=%s, animal_count=%s",
                shelter.id,
                animal_count,
            )
            return api_error(
                f"Неможливо видалити притулок: "
                f"до нього прив'язано {animal_count} тварин.",
                status.HTTP_409_CONFLICT,
            )

        shelter_id = shelter.id
        shelter.delete()

        logger.info(
            "Shelter deleted: id=%s",
            shelter_id,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)



class AnimalListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        animals = Animal.objects.all()

        search = request.query_params.get("search")
        if search:
            animals = animals.filter(
                Q(name__icontains=search) | Q(breed__icontains=search)
            )

        species = request.query_params.get("species")
        if species:
            if species not in ["dog", "cat"]:
                return api_error(
                    "Неправильний вид тварини.",
                    status.HTTP_400_BAD_REQUEST,
                )
            animals = animals.filter(species=species)

        city = request.query_params.get("city")
        if city:
            animals = animals.filter(shelter__city__icontains=city)

        shelter_id = request.query_params.get("shelter_id")
        if shelter_id:
            if not shelter_id.isdecimal() or int(shelter_id) == 0:
                return api_error(
                    "Неправильний номер притулку.",
                    status.HTTP_400_BAD_REQUEST,
                )
            animals = animals.filter(shelter_id=int(shelter_id))

        for param in ["age_min", "age_max"]:
            value = request.query_params.get(param)
            if value is not None and not value.isdecimal():
                return api_error(
                    f"Параметр {param} має бути цілим невід'ємним числом.",
                    status.HTTP_400_BAD_REQUEST,
                )

        age_min = request.query_params.get("age_min")
        age_max = request.query_params.get("age_max")

        if age_min is not None:
            animals = animals.filter(age_months__gte=int(age_min))

        if age_max is not None:
            animals = animals.filter(age_months__lte=int(age_max))

        if age_min is not None and age_max is not None and int(age_min) > int(age_max):
            return api_error(
                "Мінімальний вік не може перевищувати максимальний.",
                status.HTTP_400_BAD_REQUEST,
            )

        animal_status = request.query_params.get("status", "available")
        if animal_status not in ["available", "adopted"]:
            return api_error(
                "Неправильний статус тварини.",
                status.HTTP_400_BAD_REQUEST,
            )
        animals = animals.filter(status=animal_status)

        sort = request.query_params.get("sort", "newest")
        sort_options = {
            "newest": "-created_at",
            "age_asc": "age_months",
            "age_desc": "-age_months",
        }

        if sort not in sort_options:
            return api_error(
                "Неправильний параметр сортування.",
                status.HTTP_400_BAD_REQUEST,
            )

        animals = animals.order_by(sort_options[sort], "-id")

        serializer = AnimalSerializer(animals, many=True)
        return Response({"animals": serializer.data})

    def post(self, request):
        serializer = AnimalSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return api_error(
            "Некоректні дані тварини.",
            status.HTTP_400_BAD_REQUEST,
            serializer.errors,
        )


class AnimalDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_animal(self, pk):
        return Animal.objects.filter(pk=pk).first()

    def get(self, request, pk):
        animal = self.get_animal(pk)

        if animal is None:
            return api_error(
                "Тварину не знайдено.",
                status.HTTP_404_NOT_FOUND,
            )

        serializer = AnimalSerializer(animal)
        return Response(serializer.data)

    def patch(self, request, pk):
        animal = self.get_animal(pk)

        if animal is None:
            return api_error(
                "Тварину не знайдено.",
                status.HTTP_404_NOT_FOUND,
            )

        serializer = AnimalSerializer(
            animal,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return api_error(
            "Некоректні дані тварини.",
            status.HTTP_400_BAD_REQUEST,
            serializer.errors,
        )

    def delete(self, request, pk):
        animal = self.get_animal(pk)

        if animal is None:
            return api_error(
                "Тварину не знайдено.",
                status.HTTP_404_NOT_FOUND,
            )

        animal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShelterAnimalsAPIView(APIView):
    def get(self, request, pk):
        shelter = Shelter.objects.filter(pk=pk).first()

        if shelter is None:
            return api_error(
                "Притулок не знайдено.",
                status.HTTP_404_NOT_FOUND,
            )

        animal_status = request.query_params.get("status", "available")

        if animal_status not in ["available", "adopted"]:
            return api_error(
                "Неправильний статус тварини.",
                status.HTTP_400_BAD_REQUEST,
            )

        animals = shelter.animals.filter(status=animal_status).order_by(
            "-created_at", "-id"
        )

        serializer = AnimalSerializer(animals, many=True)
        return Response({"animals": serializer.data})
