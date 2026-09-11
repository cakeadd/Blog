from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import Article
from comments.models import Comment
from users.models import User
from users.permissions import IsBlogAdmin
from users.serializers import PasswordChangeSerializer, UserSerializer, UserUpdateSerializer

from .pagination import AdminPagination
from .admin_serializers import AdminArticleSerializer, AdminCommentSerializer
from .serializers import AdminSetupSerializer


class AdminSetupView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({
            'initialized': User.objects.filter(
                role=User.Role.ADMIN,
            ).exists(),
        })

    def post(self, request):
        if User.objects.filter(role=User.Role.ADMIN).exists():
            return Response(
                {'detail': '管理员已经初始化，不能重复注册。'},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = AdminSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            if User.objects.filter(role=User.Role.ADMIN).exists():
                return Response(
                    {'detail': '管理员已经初始化，不能重复注册。'},
                    status=status.HTTP_409_CONFLICT,
                )
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                role=User.Role.ADMIN,
            )
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'role': user.role,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminProfileView(APIView):
    permission_classes = [IsBlogAdmin]

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


class AdminPasswordChangeView(APIView):
    permission_classes = [IsBlogAdmin]

    def post(self, request):
        serializer = PasswordChangeSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '密码修改成功。'})


class AdminArticleListView(generics.ListAPIView):
    serializer_class = AdminArticleSerializer
    permission_classes = [IsBlogAdmin]
    pagination_class = AdminPagination

    def get_queryset(self):
        queryset = Article.objects.all().select_related(
            'author',
            'category',
        )
        exact_id = self.request.query_params.get('id', '').strip()
        search = self.request.query_params.get('search', '').strip()

        if exact_id:
            if not exact_id.isdigit():
                return queryset.none()
            queryset = queryset.filter(pk=int(exact_id))
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset


class AdminCommentListView(generics.ListAPIView):
    serializer_class = AdminCommentSerializer
    permission_classes = [IsBlogAdmin]
    pagination_class = AdminPagination

    def get_queryset(self):
        queryset = Comment.objects.all().select_related(
            'article',
            'author',
        )
        exact_id = self.request.query_params.get('id', '').strip()
        search = self.request.query_params.get('search', '').strip()

        if exact_id:
            if not exact_id.isdigit():
                return queryset.none()
            queryset = queryset.filter(pk=int(exact_id))
        if search:
            queryset = queryset.filter(author__username__icontains=search)
        return queryset


class AdminUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsBlogAdmin]
    pagination_class = AdminPagination

    def get_queryset(self):
        queryset = User.objects.filter(role=User.Role.USER).order_by('id')
        exact_id = self.request.query_params.get('id', '').strip()
        search = self.request.query_params.get('search', '').strip()

        if exact_id:
            if not exact_id.isdigit():
                return queryset.none()
            queryset = queryset.filter(pk=int(exact_id))
        if search:
            queryset = queryset.filter(username__icontains=search)
        return queryset


class AdminArticleDeleteView(APIView):
    permission_classes = [IsBlogAdmin]

    def delete(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        article.is_deleted = True
        article.save(update_fields=['is_deleted'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminArticleRestoreView(APIView):
    permission_classes = [IsBlogAdmin]

    def patch(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        article.is_deleted = False
        article.save(update_fields=['is_deleted'])
        return Response(AdminArticleSerializer(article).data)


class AdminCommentDeleteView(APIView):
    permission_classes = [IsBlogAdmin]

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_deleted = True
        comment.save(update_fields=['is_deleted'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminCommentRestoreView(APIView):
    permission_classes = [IsBlogAdmin]

    def patch(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_deleted = False
        comment.save(update_fields=['is_deleted'])
        return Response(AdminCommentSerializer(comment).data)


class AdminUserDeactivateView(APIView):
    permission_classes = [IsBlogAdmin]

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk, role=User.Role.USER)
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUserRestoreView(APIView):
    permission_classes = [IsBlogAdmin]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk, role=User.Role.USER)
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response(UserSerializer(user).data)
