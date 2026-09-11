from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .jwt_serializers import ActiveUserTokenRefreshSerializer, ChineseTokenObtainPairSerializer
from .serializers import (
    PasswordChangeSerializer,
    AvatarUploadSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .permissions import IsNormalUser


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class ActiveUserTokenRefreshView(TokenRefreshView):
    serializer_class = ActiveUserTokenRefreshSerializer


class ChineseTokenObtainPairView(TokenObtainPairView):
    serializer_class = ChineseTokenObtainPairSerializer


class PasswordChangeView(APIView):
    permission_classes = [IsNormalUser]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '密码修改成功。'})


class AvatarUploadView(APIView):
    permission_classes = [IsNormalUser]

    def post(self, request):
        serializer = AvatarUploadSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context={'request': request}).data)


class MeView(APIView):
    def get_permissions(self):
        if self.request.method in ('PATCH', 'DELETE'):
            return [IsNormalUser()]
        return [IsAuthenticated()]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    def delete(self, request):
        request.user.is_active = False
        request.user.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)
