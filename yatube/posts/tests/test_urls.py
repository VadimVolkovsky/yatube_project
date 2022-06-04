from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text="Текст тестового поста",
            author=cls.user
        )
        cls.list_urls = [
            '/',
            '/group/' + cls.group.slug + '/',
            '/profile/' + cls.user.username + '/',
            '/posts/' + str(cls.post.id) + '/',
            '/create/',
            '/posts/' + str(cls.post.id) + '/edit/',
            '/unexsisting_page/'
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_urls_exists_at_desired_routes_for_auth_user(self):
        status_code_list = [
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.NOT_FOUND.value,
        ]

        zip_dict = dict(zip(self.list_urls, status_code_list))

        for route, status_code in zip_dict.items():
            with self.subTest(status_code=status_code):
                response = self.authorized_client.get(route)
                self.assertEqual(response.status_code, status_code)

    def test_posts_urls_exists_at_desired_locatication_for_guest_user(self):
        """Запрошенные страницы существуют для
            неавторизованного пользователя"""
        status_code_list = [
            HTTPStatus.OK.value,  # index
            HTTPStatus.OK.value,  # group
            HTTPStatus.OK.value,  # profile
            HTTPStatus.OK.value,  # posts
            HTTPStatus.FOUND.value,  # create
            HTTPStatus.FOUND.value,  # edit
            HTTPStatus.NOT_FOUND.value,  # unexisting page
        ]
        zip_dict = dict(zip(self.list_urls, status_code_list))

        for route, status_code in zip_dict.items():
            with self.subTest(status_code=status_code):
                response = self.guest_client.get(route)
                self.assertEqual(response.status_code, status_code)

    def test_posts_urls_redirection_for_guest_client(self):
        urls = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/'
        }
        for route, redirect_page in urls.items():
            with self.subTest(redirect_page=redirect_page):
                response = self.guest_client.get(route, follow=True)
                self.assertRedirects(response, redirect_page)

    def test_post_edit_access_only_for_author(self):
        post = get_object_or_404(Post, pk=1)
        self.assertEqual(post.author.username, self.user.username)

    def test_posts_urls_uses_correct_template(self):
        urls = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/NoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in urls.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_404_page_uses_custom_template(self):
        template = 'core/404.html'
        url = '/unexsisting_page/'
        response = self.guest_client.get(url)
        self.assertTemplateUsed(response, template)
