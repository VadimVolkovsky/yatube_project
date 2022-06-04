from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с больше чем 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post))

        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_labels_have_correct_verbose_names(self):
        post = PostModelTest.post
        verbose_names_dict = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for label, verbose_name in verbose_names_dict.items():
            with self.subTest(label=label):
                response = post._meta.get_field(label).verbose_name
                self.assertEqual(response, verbose_name)

    def test_help_texts_have_correct_verbose_names(self):
        post = PostModelTest.post
        help_texts_dict = {
            'text': 'Введите описание поста',
            'group': 'Выберите наиболее подходящую группу',
        }
        for label, help_text in help_texts_dict.items():
            with self.subTest(label=label):
                response = post._meta.get_field(label).help_text
                self.assertEqual(response, help_text)
