from articles.models import Article
from comments.models import Comment
from rest_framework import serializers


class AdminArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'id', 'title', 'summary', 'content', 'author', 'author_name',
            'category', 'created_at', 'updated_at', 'is_deleted',
        )
        read_only_fields = fields

    def get_author_name(self, obj):
        return obj.author.username if obj.author.is_active else '已停用用户'


class AdminCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'article', 'author', 'author_name', 'content', 'created_at', 'is_deleted')
        read_only_fields = fields

    def get_author_name(self, obj):
        return obj.author.username if obj.author.is_active else '已停用用户'
