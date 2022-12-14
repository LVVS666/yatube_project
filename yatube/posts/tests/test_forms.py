import shutil
import tempfile


from posts.models import Post, User, Group, Comment
from posts.forms import PostForm
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title="test", slug="slug")
        cls.user = User.objects.create_user(username="auth")
        cls.post = Post.objects.create(author=cls.user, text="Текст из формы")

    def setUp(self):
        self.not_author = Client()

        self.client = Client()
        self.client.force_login(self.user)
        self.post_id = Post.objects.get(text=self.post.text)

    def test_post_create_sent_form(self):
        post_count = Post.objects.count()
        form_data = {
            "text": self.post.text,
        }
        response = self.client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile",
                              kwargs={"username": self.user.username}
                              )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(text=self.post.text).exists())

    def test_post_edit_send_form(self):
        form_data = {"text": "Новый текст"}
        response = self.client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post_id.id}),
            data=form_data,
            follow=True,
        )
        self.post.refresh_from_db()
        self.assertRedirects(
            response, reverse("posts:post_detail",
                              kwargs={"post_id": self.post_id.id}
                              )
        )
        self.assertTrue(Post.objects.filter(text=form_data["text"],
                                            id=self.post_id.id
                                            )
                        )

    def test_output_authirized_user_comment(self):
        post = Post.objects.create(text="text_one", author=self.user)
        comment = Comment.objects.create(post=post, author=self.user,
                                         text='text_comment_one'
                                         )
        comment = Comment.objects.latest('id')
        form_data = {
            'text': 'text_comment_one',
            'author': self.user,
        }
        response = self.client.get(reverse(
                                   'posts:add_comment',
                                   kwargs={'post_id': post.id}
                                   ),
                                   data=form_data,
                                   follow=True
                                   )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, form_data['author'])
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args={post.id}
                                               )
                             )

    def test_not_authorized_user_comment(self):
        post = Post.objects.create(text="text in", author=self.user)
        form_data = {'text': 'text_comment_one'}
        comment_count = Comment.objects.count()
        response = self.not_author.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}),
            data=form_data,
            follow=True)
        redirect = reverse('login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': post.id})
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertRedirects(response, redirect)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.group = Group.objects.create(title="test", slug="slug")
        cls.user = User.objects.create(username="tolik")
        cls.uploaded = SimpleUploadedFile(
            name="small.gif",
            content=(
                b"\x47\x49\x46\x38\x39\x61\x02\x00"
                b"\x01\x00\x80\x00\x00\x00\x00\x00"
                b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
                b"\x00\x00\x00\x2C\x00\x00\x00\x00"
                b"\x02\x00\x01\x00\x00\x02\x02\x0C"
                b"\x0A\x00\x3B"
            ),
            content_type="image/gif",
        )
        cls.post = Post.objects.create(
            text='text',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostImageTests.user)

    def test_image_send_index(self):
        response = self.auth_client.get(reverse("posts:index"))
        post = response.context["page_obj"][0]
        self.assertEqual(post.image, self.post.image)

    def test_image_send_group_list(self):
        response = self.auth_client.get(reverse("posts:group_list",
                                        kwargs={"slug": self.group.slug}
                                                )
                                        )
        post = response.context["page_obj"][0]
        self.assertEqual(post.image, self.post.image)

    def test_image_send_profile(self):
        response = self.auth_client.get(reverse("posts:profile",
                                        kwargs={"username": self.user}
                                                )
                                        )
        post = response.context["page_obj"][0]
        self.assertEqual(post.image, self.post.image)

    def test_image_send_post_detail(self):
        response = self.auth_client.get(reverse("posts:post_detail",
                                        kwargs={"post_id": self.post.id}
                                                )
                                        )
        post = response.context["post"]
        self.assertEqual(post.image, self.post.image)

    def test_image_output_for_pages_with_forms(self):
        post_count = Post.objects.count()
        form_data = {
            "text": "Тест формы с картинкой",
            "group": self.group.id,
            "image": PostImageTests.post.image,
        }
        response = self.auth_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", args=(PostImageTests.user.username,)),
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, "Тест формы с картинкой")
        self.assertEqual(post.group, self.group)
        self.assertIn(form_data["image"].name, self.post.image.name)
