from django.conf import settings as st
from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModel
from django.db.models import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Жанр", max_length=50, unique=True)
    description = models.TextField("Описание")

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField("Текст", help_text="Введите текст поста")
    pub_date = models.DateTimeField("Дата", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группы",
        help_text="Группа, к которой будет относиться пост",
    )
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True,
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[st.PAGE_LIMIT:]


class Comment(CreatedModel):
    post = models.ForeignKey(Post, related_name="comment",
                             verbose_name="Пост",
                             on_delete=models.CASCADE
                             )
    author = models.ForeignKey(User, related_name="comment",
                               verbose_name="Автор",
                               on_delete=models.CASCADE
                               )
    text = models.TextField("Текст комментария", max_length=50)
    created = models.DateTimeField("Дата", auto_now_add=True)

    def __str__(self):
        return self.text[0:st.PAGE_LIMIT]


class Follow(models.Model):
    user = models.ForeignKey(User, related_name="follower",
                             verbose_name="Подписчик",
                             on_delete=models.CASCADE
                             )
    author = models.ForeignKey(User, related_name="following",
                               verbose_name="Автор",
                               on_delete=models.CASCADE
                               )

    class Meta:
        constraints = [
            UniqueConstraint(fields=["user", "author"],
                             name='following_followers'
                             )
        ]
        verbose_name = "followers"
