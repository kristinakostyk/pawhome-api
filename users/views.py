
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "message": "Користувача успішно зареєстровано.",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": "Помилка реєстрації.",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

from rest_framework.permissions import IsAuthenticated


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "error": "Не передано refresh токен.",
                    "details": {
                        "refresh": ["Це поле обов'язкове."]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)

            if str(token["user_id"]) != str(request.user.id):
                return Response(
                    {
                        "error": "Токен належить іншому користувачу.",
                        "details": {},
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            token.blacklist()

        except TokenError:
            return Response(
                {
                    "error": "Недійсний або вже відкликаний refresh токен.",
                    "details": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Вихід виконано успішно."},
            status=status.HTTP_200_OK,
        )