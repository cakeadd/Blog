from django.conf import settings
from django.db import models

from articles.models import Article


class Like(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='文章',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='likes',
        verbose_name='用户',
    )
    created_at = models.DateTimeField('点赞时间', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        constraints = [
            models.UniqueConstraint(
                fields=('article', 'user'),
                name='unique_article_user_like',
            ),
        ]

    def __str__(self):
        return f'{self.user} 点赞了 {self.article}'
