
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        trim_whitespace=False,
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        max_length=128,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirmation",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "username": {"required": True, "max_length": 150},
            "first_name": {"required": False, "allow_blank": True, "max_length": 150},
            "last_name": {"required": False, "allow_blank": True, "max_length": 150},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Користувач із таким email уже існує."
            )
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirmation = attrs.get("password_confirmation")

        errors = {}

        if password != confirmation:
            errors["password_confirmation"] = [
                "Паролі не збігаються."
            ]

        user = User(
            username=attrs.get("username", ""),
            first_name=attrs.get("first_name", ""),
            last_name=attrs.get("last_name", ""),
            email=attrs.get("email", ""),
        )

        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            errors["password"] = exc.messages

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirmation")

        return User.objects.create_user(**validated_data)
