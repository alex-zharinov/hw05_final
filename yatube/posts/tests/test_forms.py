import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings

from posts.models import Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.user = User.objects.create_user(username='tester')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        TEXT = 'Тестовый текст'
        GIF_NAME = 'small.gif'
        uploaded = SimpleUploadedFile(
            name=GIF_NAME,
            content=self.small_gif,
            content_type='image/gif'
        )
        post_count = Post.objects.count()
        form_data = {
            'text': TEXT,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        username = self.user.username
        self.assertRedirects(
            response, reverse('posts:profile', args=(username,))
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEXT,
                image='posts/' + GIF_NAME,
            ).exists()
        )

    def test_edit_post(self):
        TEXT = 'Новый текст'
        GIF_NAME = 'small_1.gif'
        uploaded = SimpleUploadedFile(
            name=GIF_NAME,
            content=self.small_gif,
            content_type='image/gif',
        )
        post_count = Post.objects.count()
        post_id = self.post.id
        form_data = {
            'text': TEXT,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(post_id,)),
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Post.objects.filter(
                text=TEXT,
                image='posts/' + GIF_NAME,
            ).exists()
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=(post_id,))
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_add_comment(self):
        TEXT = 'Текст комментария'
        comments_count = Comment.objects.count()
        post_id = self.post.id
        form_data = {
            'text': TEXT
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(post_id,)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, f'/posts/{self.post.id}/'
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=TEXT,
                author=self.user,
            ).exists()
        )
