from rest_framework import serializers

from .models import Article, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('分类名称不能为空。')

        queryset = Category.objects.filter(name__iexact=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('分类名称已存在。')
        return value


class ArticleSerializer(serializers.ModelSerializer):
    content = serializers.JSONField(required=True)
    author_name = serializers.SerializerMethodField()
    summary = serializers.CharField(required=False, allow_blank=True, max_length=45)

    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'summary',
            'content',
            'author',
            'author_name',
            'category',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def get_author_name(self, obj):
        return obj.author.username if obj.author.is_active else '已停用用户'

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('文章标题不能为空。')
        if len(value) > 30:
            raise serializers.ValidationError('文章标题不能超过 30 个字符。')
        return value

    def validate_content(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('文章正文必须是 JSON 对象。')
        if value.get('format') != 'markdown':
            raise serializers.ValidationError('文章正文 format 必须为 markdown。')
        if not isinstance(value.get('body'), str):
            raise serializers.ValidationError('文章正文 body 必须是字符串。')
        return value
