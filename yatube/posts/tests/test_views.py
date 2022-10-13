from django.conf import settings as st
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test_author")
        cls.group = Group.objects.create(
            title="Test group",
            slug="test_group",
            description="Test group",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text="Test post group",
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_info(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)

    def test_index_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse("posts:index"))
        post = response.context["page_obj"][0]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pub_date, self.post.pub_date)

    def test_values_group_context_first(self):
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        post = response.context["page_obj"][0]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertIsInstance(response.context["group"], Group)

    def test_values_profile_context_first(self):
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user})
        )
        post = response.context["page_obj"][0]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertIsInstance(response.context["author"], User)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertIn("post", response.context)
        post = response.context["post"]
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pub_date, self.post.pub_date)

    def test_post_create_page_show_correct_context(self,):
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            form_field = response.context.get("form").fields.get(value)
            self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context["is_edit"], False)
        self.assertIsInstance(response.context.get("form"), PostForm)

    def test_post_edit_page_show_correct_context(self,):
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={'post_id': self.post.id})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            form_field = response.context.get("form").fields.get(value)
            self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context["is_edit"], True)
        self.assertIsInstance(response.context.get("form"), PostForm)


class PaginatorViewsTest(PostPagesTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(st.POST_LIMIT):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f"Тest post {i}",
                group=cls.group,
            )

    def test_first_page_ten_posts(self):
        posts_on_page = (
            self.authorized_client.get(reverse("posts:index")),
            self.authorized_client.get(
                reverse("posts:group_list", kwargs={"slug": self.group.slug})
            ),
            self.authorized_client.get(
                reverse("posts:profile", kwargs={"username": self.user})
            ),
        )
        for response in posts_on_page:
            with self.subTest(response=response):
                self.assertEqual
                (len(response.context["page_obj"]), st.POST_LIMIT)

    def test_index_second_page_three_posts(self):
        posts_on_page = (
            self.authorized_client.get(reverse("posts:index") + "?page=2"),
            self.authorized_client.get(
                reverse("posts:group_list", kwargs={"slug": self.group.slug})
                + "?page=2",
            ),
            self.authorized_client.get(
                reverse("posts:profile", kwargs={"username": self.user})
                + "?page=2",
            ),
        )
        for response in posts_on_page:
            with self.subTest(response=response):
                self.assertEqual(len(response.context["page_obj"]), 1)


class PostPageViewsTest(PostPagesTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_first = Group.objects.create(
            title="Тестовая группа one",
            slug="test_slug_one",
            description="Тестовое описание one",
        )

    def test_post_added_and_not_group(self):
        response_index = self.authorized_client.get(reverse("posts:index"))
        response_group = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test_group"})
        )
        response_profile = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user})
        )
        response_not_group = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test_slug_one"})
        )

        index = response_index.context["page_obj"]
        group = response_group.context["page_obj"]
        profile = response_profile.context["page_obj"]
        not_group = response_not_group.context["page_obj"]
        self.assertIn(self.post, index,
                      "Ошибка - поста нет на главной странице"
                      )
        self.assertIn(self.post, group, "Ошибка - поста нет в группе")
        self.assertIn(self.post, profile, "Ошибка - поста нет в профайле")
        self.assertNotIn(self.post, not_group, "Ошибка - пост есть в группе")
