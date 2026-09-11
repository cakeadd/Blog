from rest_framework import generics

from .models import Article
from .pagination import ArticlePagination
from .permissions import IsArticleAuthorOrReadOnly
from .serializers import ArticleSerializer


class ArticleListCreateView(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsArticleAuthorOrReadOnly]
    pagination_class = ArticlePagination

    def get_queryset(self):
        queryset = Article.objects.filter(is_deleted=False).select_related(
            'author',
            'category',
        )
        category_keyword = self.request.query_params.get('category', '').strip()
        title_keyword = self.request.query_params.get('title', '').strip()
        author_id = self.request.query_params.get('author', '').strip()
        if category_keyword:
            queryset = queryset.filter(category__name__icontains=category_keyword)
        if title_keyword:
            queryset = queryset.filter(title__icontains=title_keyword)
        if author_id.isdigit():
            queryset = queryset.filter(author_id=int(author_id))
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.filter(is_deleted=False).select_related(
        'author',
        'category',
    )
    serializer_class = ArticleSerializer
    permission_classes = [IsArticleAuthorOrReadOnly]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
