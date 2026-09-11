from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.permissions import IsNormalUser


class IsArticleAuthorOrReadOnly(BasePermission):
    message = '你只能修改或删除自己发布的文章。'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsNormalUser().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.id


class IsNormalUserOrReadOnly(BasePermission):
    message = '只有普通用户可以执行此操作。'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsNormalUser().has_permission(request, view)
