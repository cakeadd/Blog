from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import Article
from articles.pagination import ArticlePagination
from articles.serializers import ArticleSerializer

from .models import Like
from users.permissions import IsNormalUser


class MyLikeListView(APIView):
    permission_classes = [IsNormalUser]
    pagination_class = ArticlePagination

    def get(self, request):
        queryset = Article.objects.filter(
            likes__user=request.user,
            is_deleted=False,
        ).select_related('author', 'category').order_by('-likes__created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ArticleSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ArticleLikeView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsNormalUser()]

    def get_article(self, article_id):
        return get_object_or_404(Article, pk=article_id, is_deleted=False)

    def get(self, request, article_id):
        article = self.get_article(article_id)
        liked = (
            request.user.is_authenticated
            and request.user.role == request.user.Role.USER
            and Like.objects.filter(article=article, user=request.user).exists()
        )
        return Response({
            'liked': liked,
            'likes_count': Like.objects.filter(article=article).count(),
        })

    def post(self, request, article_id):
        article = self.get_article(article_id)
        like, created = Like.objects.get_or_create(
            article=article,
            user=request.user,
        )
        return Response(
            {
                'liked': True,
                'likes_count': Like.objects.filter(article=article).count(),
                'like_id': like.id,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, article_id):
        article = self.get_article(article_id)
        Like.objects.filter(article=article, user=request.user).delete()
        return Response({
            'liked': False,
            'likes_count': Like.objects.filter(article=article).count(),
        })
