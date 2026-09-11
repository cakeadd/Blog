from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.permissions import IsNormalUser


class IsCommentAuthorOrReadOnly(BasePermission):
    message = '你只能删除自己的评论。'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsNormalUser().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.id
