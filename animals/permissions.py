
from rest_framework.permissions import BasePermission


class IsAdminForShelterDelete(BasePermission):
    message = "Видаляти притулки може лише адміністратор."

    def has_permission(self, request, view):
        if request.method != "DELETE":
            return True

        return (
            request.user.is_authenticated
            and request.user.is_staff
        )
