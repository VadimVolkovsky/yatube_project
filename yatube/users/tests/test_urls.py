from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='NoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_users_urls_exist_at_desired_locations_for_auth_client(self):
        urls = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
            '/auth/password_reset_form/': HTTPStatus.OK.value,
            '/auth/password_change/': HTTPStatus.OK.value,
            '/auth/password_change/done/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
        }

        for route, status_code in urls.items():
            with self.subTest(status_code=status_code):
                response = self.authorized_client.get(route)
                self.assertEqual(response.status_code, status_code)

    def test_users_urls_uses_correct_templates(self):
        urls = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset_form/': 'users/password_reset_form.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for route, template in urls.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(route)
                self.assertTemplateUsed(response, template)
