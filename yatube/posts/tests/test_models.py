from django.conf import settings as st
from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

    def test_models_have_correct_object_names(self):
        field_context = {
            self.post.text[st.PAGE_LIMIT:]: str(self.post),
            self.group.title: str(self.group),
        }
        for str_key, str_value in field_context.items():
            self.assertEqual(str_key, str_value)

    def test_verbose_name_post(self):
        post = PostModelTest.post
        field_verbose = {
            "author": "Автор",
            "group": "Группы",
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_text_help_post(self):
        post = PostModelTest.post
        field_help = {
            "text": "Введите текст поста",
            "group": "Группа, к которой будет относиться пост",
        }
        for field, expected_value in field_help.items():
            with self.subTest(field=field):
                self.assertEqual
                (post._meta.get_field(field).help_text, expected_value)
