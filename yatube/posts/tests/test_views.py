from django.conf import settings as st
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django import forms
from posts.models import Group, Post, Follow
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
            text="Test post",
        )
        cls.new_author = User.objects.create(username="new_author")

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def Equal_test_context(self, first_context, second_context):
        self.assertEqual(first_context.author, second_context.author)
        self.assertEqual(first_context.text, second_context.text)
        self.assertEqual(first_context.group, second_context.group)

    def test_follow(self):
        count_follow = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.new_author})
        )
        follow = Follow.objects.last()
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author, self.new_author)
        self.assertEqual(follow.user, self.user)

    def test_unfollow(self):
        count_follow = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.new_author}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.new_author}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_following_posts(self):
        new_user = User.objects.create(username='leo')
        authorized_client = Client()
        authorized_client.force_login(new_user)
        authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username})
        )
        response_follow = authorized_client.get(reverse('posts:follow_index'))
        if 'page_obj' not in response_follow.context:
            post = response_follow.context['post']
        else:
            self.assertEqual(len(response_follow.context['page_obj']), 1)
            post = response_follow.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.id, self.post.id)

    def test_unfollowing_posts(self):
        response_unfollow = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        context_unfollow = response_unfollow.context
        self.assertEqual(len(context_unfollow['page_obj']), 0)

    def check_post_info(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)

    def test_index_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse("posts:index"))
        post = response.context["page_obj"][0]
        self.Equal_test_context(post, self.post)
        self.assertEqual(post.pub_date, self.post.pub_date)

    def test_values_group_context_first(self):
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        post = response.context["page_obj"][0]
        self.Equal_test_context(post, self.post)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertIsInstance(response.context["group"], Group)

    def test_values_profile_context_first(self):
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user})
        )
        post = response.context["page_obj"][0]
        self.Equal_test_context(post, self.post)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertIsInstance(response.context["author"], User)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertIn("post", response.context)
        post = response.context["post"]
        self.Equal_test_context(post, self.post)
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


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test_author")
        cls.group = Group.objects.create(
            title="Test group",
            slug="test_group",
            description="Test group",
        )
        for i in range(st.POST_LIMIT):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f"Тest post {i}",
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
                self.assertEqual(len(response.context["page_obj"]),
                                 st.POST_LIMIT
                                 )


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


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test_author")
        cls.group = Group.objects.create(
            title="Test group",
            slug="test_group",
            description="Test group",
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_cashe(self):
        posts = Post.objects.all()
        posts.delete()
        cache.clear()
        new_post = Post.objects.create(
            text='text_test_post_cache.',
            author=self.user,
            group=self.group
        )
        post_count = Post.objects.count()
        response = self.authorized_client.get(reverse('posts:index'))
        cached_response_content = response.content
        new_post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(Post.objects.count(), post_count - 1)
        self.assertEqual(cached_response_content, response.content)
        cache.clear()
        response_two = self.authorized_client.get('posts:index')
        self.assertNotEqual(cached_response_content, response_two.content)
