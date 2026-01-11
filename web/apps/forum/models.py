from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Reaction(models.Model):
    LIKE = 1
    DISLIKE = -1
    CHOICES = ((LIKE, 'Like'), (DISLIKE, 'Dislike'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=CHOICES)

    # Generic relation чтобы ставить реакции на что угодно
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')


# === НОВОСТИ ===
class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")  # Summernote
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    reactions = GenericRelation(Reaction)

    def get_likes(self):
        return self.reactions.filter(value=1).count()

    def get_dislikes(self):
        return self.reactions.filter(value=-1).count()


class NewsComment(models.Model):
    news = models.ForeignKey(News, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE,
                               verbose_name="Родитель")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reactions = GenericRelation(Reaction)

    def get_likes(self):
        return self.reactions.filter(value=1).count()

    def get_dislikes(self):
        return self.reactions.filter(value=-1).count()


# === ФОРУМ ===
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    is_admin_only = models.BooleanField(default=False, verbose_name="Блок администрации")
    is_feedback = models.BooleanField(default=False, verbose_name="Связь с администрацией")

    def __str__(self):
        return self.name


class Thread(models.Model):
    category = models.ForeignKey(Category, related_name='threads', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()  # Первый пост темы
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    reactions = GenericRelation(Reaction)

    def get_likes(self):
        return self.reactions.filter(value=1).count()

    def get_dislikes(self):
        return self.reactions.filter(value=-1).count()


class ThreadPost(models.Model):
    thread = models.ForeignKey(Thread, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # НОВОЕ ПОЛЕ
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE, verbose_name="Родитель")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reactions = GenericRelation(Reaction)

    def get_likes(self):
        return self.reactions.filter(value=1).count()

    def get_dislikes(self):
        return self.reactions.filter(value=-1).count()

class ChatMessage(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}: {self.content[:20]}"