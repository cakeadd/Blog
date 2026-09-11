from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', '普通用户'
        ADMIN = 'admin', '管理员'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username
