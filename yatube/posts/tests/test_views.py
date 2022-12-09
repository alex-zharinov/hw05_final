import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.cache import cache

from posts.models import Group, Post, User, Follow


TEST_POST_ON_PAGE = 12
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.image = 'posts/small.gif'
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый тест',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def check_post_fields(self, test_post):
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.image, self.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'tester'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': 1}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.check_post_fields(response.context['page_obj'][0])

    def test_group_list_context(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug'})
        )
        self.check_post_fields(response.context['page_obj'][0])

    def test_group_list_post_not(self):
        group_0 = Group.objects.create(
            title='Тестовая группа 0',
            slug='slug0',
            description='Тестовое описание 0',
        )
        post_0 = Post.objects.create(
            text='Тестовый тест',
            author=self.user,
            group=group_0,
        )
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug'})
        )
        self.assertFalse(
            post_0 in response.context['page_obj']
        )

    def test_profile_context(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'tester'})
        )
        self.check_post_fields(response.context['page_obj'][0])

    def test_detail_context(self):
        response = self.guest_client.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.check_post_fields(response.context['post'])

    def test_post_create_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        post = Post.objects.get(id=1)
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=(post.id,))
        )
        form_value = {
            'text': post.text,
            'group': post.group.id,
            'image': post.image,
        }
        for value, expected in form_value.items():
            with self.subTest(value=value):
                form_value = response.context['form'].initial[value]
                self.assertEqual(form_value, expected)

    def test_pages_paginator_context(self):
        post_list = []
        for index in range(TEST_POST_ON_PAGE):
            post_list.append(
                Post(
                    text=f'Тестовый пост {index}',
                    author=self.user,
                    group=self.group,
                )
            )
        Post.objects.bulk_create(post_list)
        pages_list = {
            'posts:index': {},
            'posts:group_list': {'slug': 'slug'},
            'posts:profile': {'username': 'tester'},
        }
        for view, param in pages_list.items():
            with self.subTest(param=param):
                response = self.guest_client.get(
                    reverse(view, kwargs=param)
                )
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.guest_client.get(
                    reverse(view, kwargs=param) + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_guest_add_comment(self):
        '''Добавление комментария неавторизированного пользователя'''
        response = self.guest_client.get(
            reverse('posts:add_comment', args=(self.post.id,))
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )

    def test_cache_index_page(self):
        new_post = Post.objects.create(
            text='New post',
            author=self.user
        )
        actual_page = self.authorized_client.get(
            reverse('posts:index')
        ).content
        new_post.delete()
        cached_page = self.authorized_client.get(
            reverse('posts:index')
        ).content
        self.assertEqual(actual_page, cached_page)
        cache.clear()
        cleared_page = self.authorized_client.get(
            reverse('posts:index')
        ).content
        self.assertNotEqual(actual_page, cleared_page)

    def test_follow(self):
        user = User.objects.create_user(username='username')
        authorized_client = Client()
        authorized_client.force_login(user)
        authorized_client.get(
            reverse('posts:profile_follow', args=(self.user.username,))
        )
        self.assertTrue(
            Follow.objects.filter(
                user=user
            ).filter(
                author=self.user
            ).exists()
        )
        authorized_client.get(
            reverse('posts:profile_unfollow', args=(self.user.username,))
        )
        self.assertFalse(
            Follow.objects.filter(
                user=user
            ).filter(
                author=self.user
            ).exists()
        )

    def test_new_post_to_followers(self):
        user = User.objects.create_user(username='username')
        authorized_client = Client()
        authorized_client.force_login(user)
        Follow.objects.create(
            user=self.user,
            author=user
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        actual_count = len(response.context['page_obj'])
        Post.objects.create(
            text='Text',
            author=user,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        new_count = len(response.context['page_obj'])
        self.assertTrue(
            new_count == actual_count + 1
        )

    def test_new_post_not_followers(self):
        user = User.objects.create_user(username='username')
        authorized_client = Client()
        authorized_client.force_login(user)
        Follow.objects.create(
            user=self.user,
            author=user
        )
        response = authorized_client.get(
            reverse('posts:follow_index')
        )
        actual_count = len(response.context['page_obj'])
        Post.objects.create(
            text='Text',
            author=user,
        )
        response = authorized_client.get(
            reverse('posts:follow_index')
        )
        new_count = len(response.context['page_obj'])
        self.assertEqual(actual_count, new_count)
