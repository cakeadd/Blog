from django.shortcuts import get_object_or_404
from rest_framework import generics

from articles.models import Article

from .models import Comment
from .permissions import IsCommentAuthorOrReadOnly
from .serializers import CommentSerializer


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsCommentAuthorOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        return Comment.objects.filter(
            article_id=self.kwargs['article_id'],
            is_deleted=False,
            article__is_deleted=False,
        ).select_related('article', 'author')

    def perform_create(self, serializer):
        article = get_object_or_404(
            Article,
            pk=self.kwargs['article_id'],
            is_deleted=False,
        )
        serializer.save(article=article, author=self.request.user)


class CommentDetailView(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.filter(is_deleted=False).select_related(
        'article',
        'author',
    )
    serializer_class = CommentSerializer
    permission_classes = [IsCommentAuthorOrReadOnly]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
