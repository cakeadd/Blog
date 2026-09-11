from django.urls import path

from .views import CommentDetailView, CommentListCreateView

urlpatterns = [
    path(
        'articles/<int:article_id>/comments/',
        CommentListCreateView.as_view(),
        name='comment-list-create',
    ),
    path(
        'comments/<int:pk>/',
        CommentDetailView.as_view(),
        name='comment-detail',
    ),
]
