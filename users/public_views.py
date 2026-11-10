from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import Article
from articles.pagination import ArticlePagination
from articles.serializers import ArticleSerializer
from likes.models import Like

from .models import User
from .serializers import PublicUserSerializer


class PublicUserDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return Response(PublicUserSerializer(user).data)


class PublicUserLikeListView(APIView):
    permission_classes = [AllowAny]
    pagination_class = ArticlePagination

    def get(self, request, user_id):
        queryset = Article.objects.filter(
            likes__user_id=user_id,
            is_deleted=False,
        ).select_related('author', 'category').order_by('-likes__created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            ArticleSerializer(page, many=True).data,
        )
