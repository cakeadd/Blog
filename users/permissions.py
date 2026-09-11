from rest_framework.permissions import BasePermission

from .models import User


class IsNormalUser(BasePermission):
    message = '只有普通用户可以执行此操作。'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == User.Role.USER
        )


class IsBlogAdmin(BasePermission):
    message = '只有管理员可以执行此操作。'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == User.Role.ADMIN
        )
