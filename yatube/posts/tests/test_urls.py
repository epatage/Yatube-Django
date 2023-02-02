from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class GroupAndPostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        # Создаем авторизированного пользователя (не автора)
        cls.user_not_auth = User.objects.create_user(username='HasNoName')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Комментарий',
            post=cls.post,
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client_auth = Client()
        self.authorized_client_auth.force_login(self.user)

        self.authorized_client_not_auth = Client()
        self.authorized_client_not_auth.force_login(self.user_not_auth)

    def test_urls_exists_for_all_users_with_HTTPStatus_OK(self):
        """URL-адреса доступны всем пользователям."""
        url_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/',
        )

        for address in url_names:
            with self.subTest(address=address):
                # Проверка для не авторизированного пользователя
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                # Проверка для авторизированного пользователя
                response = self.authorized_client_auth.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_only_authorized_user_with_HTTPStatus_OK(self):
        """URL-адреса доступны только авторизированному пользователю."""
        url_names = (
            f'/posts/{self.post.id}/edit/',
            '/create/',
        )

        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client_auth.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_all_users_with_HTTPStatus_NOT_FOUND(self):
        """URL-адреса вернут 404 всем пользователям."""
        url_names = (
            '/unexisting_page/',
        )

        for address in url_names:
            with self.subTest(address=address):
                # Проверка для не авторизированного пользователя
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                # Проверка для авторизированного пользователя
                response = self.authorized_client_auth.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_post_id_edit_url_exists_at_desired_location(self):
        """Страница '/posts/post_id/edit/' перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/',
            follow=True,
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
        )

    def test_posts_post_id_edit_url_exists_authorized(self):
        """Страница '/posts/post_id/edit/' перенаправит авторизованного
        пользователя не автора на страницу детальной информации поста.
        """
        response = self.authorized_client_not_auth.get(
            f'/posts/{self.post.id}/edit/',
            follow=True,
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_posts_create_url_exists_at_desired_location(self):
        """Страница '/create/' перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/group/nonexistent/': 'core/404.html',  # Не существующая стр.
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_auth.get(address)
                self.assertTemplateUsed(response, template)
