from django.urls import path

from .views import ArticleLikeView, MyLikeListView

urlpatterns = [
    path('likes/', MyLikeListView.as_view(), name='my-like-list'),
    path(
        'articles/<int:article_id>/like/',
        ArticleLikeView.as_view(),
        name='article-like',
    ),
]
