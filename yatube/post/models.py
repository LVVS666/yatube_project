# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    # Модель групп
    title = models.CharField(max_length=20)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="groups",
    )
