from django.urls import path

from .views import (
    AdminSetupView,
    AdminProfileView,
    AdminPasswordChangeView,
    AdminArticleListView,
    AdminArticleDeleteView,
    AdminArticleRestoreView,
    AdminCommentListView,
    AdminCommentDeleteView,
    AdminCommentRestoreView,
    AdminUserListView,
    AdminUserDeactivateView,
    AdminUserRestoreView,
)

urlpatterns = [
    path('setup/', AdminSetupView.as_view()),
    path('profile/', AdminProfileView.as_view()),
    path('password/', AdminPasswordChangeView.as_view()),
    path('articles/', AdminArticleListView.as_view()),
    path('articles/<int:pk>/', AdminArticleDeleteView.as_view()),
    path('articles/<int:pk>/restore/', AdminArticleRestoreView.as_view()),
    path('comments/', AdminCommentListView.as_view()),
    path('comments/<int:pk>/', AdminCommentDeleteView.as_view()),
    path('comments/<int:pk>/restore/', AdminCommentRestoreView.as_view()),
    path('users/', AdminUserListView.as_view()),
    path('users/<int:pk>/', AdminUserDeactivateView.as_view()),
    path('users/<int:pk>/restore/', AdminUserRestoreView.as_view()),
]
