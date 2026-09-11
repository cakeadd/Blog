from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active', 'date_joined', 'avatar_url')
        read_only_fields = ('id', 'role', 'is_active', 'date_joined')

    def get_avatar_url(self, obj):
        return obj.avatar.url if obj.avatar else None


class PublicUserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_active', 'date_joined', 'avatar_url')
        read_only_fields = fields

    def get_username(self, obj):
        return obj.username if obj.is_active else '已停用用户'

    def get_avatar_url(self, obj):
        return obj.avatar.url if obj.avatar else None


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

    def validate_avatar(self, value):
        if value.size > 3 * 1024 * 1024:
            raise serializers.ValidationError('头像图片大小不能超过 3MB。')
        if value.image.format not in ('JPEG', 'PNG'):
            raise serializers.ValidationError('头像只能使用 JPG 或 PNG 图片。')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.avatar = self.validated_data['avatar']
        user.save(update_fields=['avatar'])
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        queryset = User.objects.filter(username__iexact=value).exclude(
            pk=self.instance.pk,
        )
        if queryset.exists():
            raise serializers.ValidationError('用户名已存在。')
        return value


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('旧密码不正确。')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次输入的新密码不一致。'})
        return attrs

    def save(self, **kwargs):
        self.instance.set_password(self.validated_data['new_password'])
        self.instance.save(update_fields=['password'])
        return self.instance


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('用户名已存在。')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致。'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)
