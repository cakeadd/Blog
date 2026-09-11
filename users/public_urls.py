from django.urls import path

from .public_views import PublicUserDetailView, PublicUserLikeListView

urlpatterns = [
    path('<int:pk>/', PublicUserDetailView.as_view(), name='public-user-detail'),
    path('<int:user_id>/likes/', PublicUserLikeListView.as_view(), name='public-user-likes'),
]
