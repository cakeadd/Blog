from django.urls import path
from .views import (
    ActiveUserTokenRefreshView,
    AvatarUploadView,
    ChineseTokenObtainPairView,
    MeView,
    PasswordChangeView,
    RegisterView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', ChineseTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', ActiveUserTokenRefreshView.as_view(), name='token-refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('password/', PasswordChangeView.as_view(), name='password-change'),
    path('avatar/', AvatarUploadView.as_view(), name='avatar-upload'),
]
