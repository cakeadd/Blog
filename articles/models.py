from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField('分类名称', max_length=100, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = '分类'
        verbose_name_plural = '分类'

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField('标题', max_length=30)
    summary = models.TextField('摘要', blank=True)
    content = models.JSONField('正文', default=dict)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name='作者',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name='分类',
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', null=True, blank=True)
    is_deleted = models.BooleanField('是否已删除', default=False)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = '文章'
        verbose_name_plural = '文章'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
            update_fields = kwargs.get('update_fields')
            if update_fields is not None:
                kwargs['update_fields'] = set(update_fields) | {'updated_at'}
        super().save(*args, **kwargs)
