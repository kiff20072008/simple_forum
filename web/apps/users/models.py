from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_banned = models.BooleanField(default=False, verbose_name="Забанен")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")

    def is_moderator(self):
        return self.groups.filter(name='Moderators').exists() or self.is_superuser