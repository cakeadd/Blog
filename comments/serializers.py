from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'article', 'author', 'author_name', 'content', 'created_at')
        read_only_fields = ('id', 'article', 'author', 'created_at')

    def get_author_name(self, obj):
        return obj.author.username if obj.author.is_active else '已停用用户'

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError('评论内容不能为空。')
        return value
