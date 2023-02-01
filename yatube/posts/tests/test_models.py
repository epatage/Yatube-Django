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
            text='Тестовый пост',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post

        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(post.group.title, 'Тестовая группа')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post

        verbose_name_author = post._meta.get_field('author').verbose_name
        self.assertEqual(verbose_name_author, 'Автор')

        verbose_name_group = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose_name_group, 'Группа')

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post

        help_text_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text_text, 'Введите текст поста')

        help_text_group = post._meta.get_field('group').help_text
        self.assertEqual(
            help_text_group, 'Группа, к которой будет относиться пост'
        )
