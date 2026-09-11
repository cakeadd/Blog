from django.conf import settings
from django.db import models

from articles.models import Article


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='文章',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='comments',
        verbose_name='作者',
    )
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_deleted = models.BooleanField('是否已删除', default=False)

    class Meta:
        ordering = ('created_at',)
        verbose_name = '评论'
        verbose_name_plural = '评论'

    def __str__(self):
        return f'{self.author}：{self.content[:30]}'
