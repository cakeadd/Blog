from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class AdminSetupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('用户名不能为空。')
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('用户名已存在。')
        return value
