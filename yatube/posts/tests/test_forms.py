import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_created_successfully(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста из формы',
            'author': self.user,
            'image': self.picture,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_eddited_successfully(self):
        form_data = {
            'text': 'Текст поста из формы',
            'author': self.user
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        form_data = {
            'text': 'Новый текст поста из формы',
            'author': self.authorized_client
        }
        last_post = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': last_post}),
            is_edit=True,
            data=form_data,
            follow=True
        )
        last_post_text_eddited = Post.objects.get(id=last_post).text
        self.assertEqual(last_post_text_eddited, 'Новый текст поста из формы')

    def test_comment_for_post_created_successfully(self):
        """Тест создания комментария авторизованным пользователем"""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        form_data = {
            'post': post,
            'author': self.user,
            'text': 'Тестовый комментарий'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(post.comments.filter(text=form_data['text']).exists())

    def test_guest_client_cannot_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста из формы',
            'author': self.guest_client,
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_client_cannot_create_comment_for_post(self):
        Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        form_data = {
            'text': 'Тестовый комментарий',
            'author': self.guest_client,
        }
        post_id = Post.objects.count()
        comments_count = Comment.objects.count()
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
