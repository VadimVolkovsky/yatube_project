import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Follow, Group, Post

from yatube.settings import LIMIT_FOR_POSTS

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_2 = User.objects.create_user(username='NoName2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.POSTS_ON_FIRST_PAGE = LIMIT_FOR_POSTS
        cls.POSTS_ON_SECOND_PAGE = 4
        bulk_of_posts = cls.POSTS_ON_FIRST_PAGE + cls.POSTS_ON_SECOND_PAGE
        picture_jpg_in_byte = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.picture = SimpleUploadedFile(
            name='picture.jpg',
            content=picture_jpg_in_byte,
            content_type='image/jpg'
        )

        objs = [
            Post(
                text='Текст тестового поста',
                group=cls.group,
                author=cls.user,
                image=cls.picture
            )
            for obj in range(bulk_of_posts)
        ]
        Post.objects.bulk_create(objs, batch_size=bulk_of_posts)
        cls.test_post = Post.objects.get(id=1)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_templates(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                    'username': self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                    'post_id': self.test_post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                    'post_id': self.test_post.id}): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_templates_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом"""
        urls = {
            'posts:index': None,
            'posts:group_list': {'slug': self.group.slug},
            'posts:profile': {'username': self.user.username},
        }
        for url_name, data in urls.items():
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(
                    reverse(url_name, kwargs=data))
                self.assertEqual(response.context
                                 ['page_obj'][0].text,
                                 self.test_post.text)
                self.assertEqual(response.context
                                 ['page_obj'][0].group.title,
                                 self.group.title)
                self.assertEqual(response.context
                                 ['page_obj'][0].author.username,
                                 self.user.username)
                self.assertTrue(response.context['page_obj'][0].image.name)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.test_post.id}))
        post = response.context['page_obj']
        self.assertEqual(post.text, self.test_post.text)
        self.assertEqual(post.group.title, self.group.title)
        self.assertEqual(post.author.username, self.user.username)
        self.assertTrue(response.context['page_obj'].image.name)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.test_post.id}))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_create_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_paginator_shows_correct_number_of_posts_per_page(self):
        urls = {
            'posts:index': None,
            'posts:group_list': {'slug': self.group.slug},
            'posts:profile': {'username': self.user.username},
        }
        for url, data in urls.items():
            with self.subTest(url=url):
                response_1 = self.authorized_client.get(reverse(
                    url, kwargs=data))
                response_2 = self.authorized_client.get(reverse(
                    url, kwargs=data) + '?page=2')
                self.assertEqual(len(
                    response_1.context['page_obj']), self.POSTS_ON_FIRST_PAGE)
                self.assertEqual(len(
                    response_2.context['page_obj']), self.POSTS_ON_SECOND_PAGE)

    def test_index_page_caches_posts(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            text='Текст тестового поста',
            author=self.user
        )
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_2.content, response_3.content)

    def test_auth_user_can_follow_author(self):
        """Авторизованный пользователь может
        подписаться/отписаться на/от автора"""
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user_2}))
        following = Follow.objects.filter(user=self.user, author=self.user_2)
        self.assertTrue(following)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.user_2}))
        unfollowing = Follow.objects.filter(user=self.user, author=self.user_2)
        self.assertFalse(unfollowing)

    def test_followers_can_see_new_posts_of_authors_they_follow(self):
        """Пользователи видят в ленте (в разделе избранные авторы) посты авторов,
         на которых они подписаны"""
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.authorized_client_2.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user}))
        response = self.authorized_client_2.get(reverse('posts:follow_index'))
        self.assertEqual(len(
            response.context['page_obj']), self.POSTS_ON_FIRST_PAGE)
        self.assertEqual(
            response.context['page_obj'][0].author.username,
            self.user.username)
