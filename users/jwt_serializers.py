from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class ActiveUserTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        user_id = refresh.get(api_settings.USER_ID_CLAIM)
        user_lookup = {api_settings.USER_ID_FIELD: user_id}
        if not User.objects.filter(**user_lookup, is_active=True).exists():
            raise InvalidToken('用户已停用，无法刷新访问令牌。')
        return super().validate(attrs)


class ChineseTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': '用户名或密码错误。',
    }
