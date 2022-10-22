from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.not_author = User.objects.create_user(username="NotAuthor")
        cls.url_context = {
            "/": HTTPStatus.OK,
            "/note": HTTPStatus.NOT_FOUND,
            f"/group/{cls.group.slug}/": HTTPStatus.OK,
            f"/profile/{cls.user}/": HTTPStatus.OK,
            f"/posts/{cls.post.id}": HTTPStatus.MOVED_PERMANENTLY,
            f"/posts/{cls.post.id}/edit/": HTTPStatus.OK,
            "/create": HTTPStatus.MOVED_PERMANENTLY,
            "/follow/": HTTPStatus.OK,
            f"/posts/{cls.post.id}/comment/": HTTPStatus.FOUND,
            f"/profile/{cls.user}/follow/": HTTPStatus.FOUND,
            f"/profile/{cls.user}/unfollow/": HTTPStatus.FOUND,
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

        self.authorized_client_but_not_author = Client()
        self.authorized_client_but_not_author.force_login(self.not_author)

    def test_url_guest(self):
        self.url_context[f"/posts/{self.post.id}/edit/"] = HTTPStatus.FOUND
        self.url_context["/follow/"] = HTTPStatus.FOUND
        self.url_context[f"/profile/{self.user}/follow/"] = HTTPStatus.FOUND
        self.url_context[f"/profile/{self.user}/unfollow/"] = HTTPStatus.FOUND
        for url, status_code in self.url_context.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_url_authorized(self):
        for url, status_code in self.url_context.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_post_edit_url_redirect_not_author(self):
        response = self.authorized_client_but_not_author.get(
            f"/posts/{self.post.id}/edit/", follow=True
        )
        self.assertRedirects(response, f"/posts/{self.post.id}/")

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            f"/posts/{self.post.id}/edit/": "posts/create_post.html",
            f"/profile/{self.user}/": "posts/profile.html",
            "/create/": "posts/create_post.html",
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
