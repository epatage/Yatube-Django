import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class GroupAndPostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.user_follower = User.objects.create_user(username='follower')
        cls.user_not_follower = User.objects.create_user(
            username='not_follower'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.additional_group = Group.objects.create(
            title='Тестовая группа №2',
            slug='test-slug-2',
            description='Тестовое описание',
        )

        # Картинка для тестирования
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        # Создаем 10 постов с одной группой
        for i in range(10):
            Post.objects.create(
                author=cls.author,
                text=f'Тестовый пост {i}',
                group=cls.group,
            )
        # Дополнительный пост к постам из цикла (ссылка для тестов)
        cls.additional_post_for_test = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )

        # Отдельный пост с другой группой (ссылка для тестов)
        cls.post_with_additional_group = Post.objects.create(
            author=cls.author,
            text='Тестовый пост с группой',
            group=cls.additional_group,
            image=uploaded,
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        self.authorized_client_follower = Client()
        self.authorized_client_follower.force_login(self.user_follower)

        self.authorized_client_not_follower = Client()
        self.authorized_client_not_follower.force_login(self.user_not_follower)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    # def tearDown(self):
    #     cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.additional_post_for_test.id},
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.additional_post_for_test.id},
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj']
        for post in first_object:
            if post.id == self.additional_post_for_test.id:
                test_post = post

                post_group_0 = test_post.group.title
                post_text_0 = test_post.text
                post_author_0 = test_post.author.username
                # Добавлена проверка изображения
                post_image_0 = test_post.image

                self.assertEqual(
                    post_group_0,
                    self.additional_post_for_test.group.title,
                )
                self.assertEqual(
                    post_text_0,
                    self.additional_post_for_test.text,
                )
                self.assertEqual(
                    post_author_0,
                    self.additional_post_for_test.author.username,
                )
                # Добавлена проверка изображения
                self.assertEqual(
                    post_image_0,
                    self.additional_post_for_test.image,
                )

    def test_first_page_index_contains_ten_records(self):
        """Количество постов на первой странице index равно 10."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_one_records(self):
        """Количество постов на второй странице index равно двум."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(
                reverse(
                    'posts:group_list', kwargs={'slug': self.group.slug}
                )))
        posts_group_list = response.context['page_obj']
        for post in posts_group_list:
            with self.subTest(post=post):
                self.assertEqual(post.group.title, self.group.title)

                # Добавлена проверка передачи картинки в контекст
                if post.id == self.additional_post_for_test.id:
                    self.assertEqual(
                        post.image,
                        self.additional_post_for_test.image,
                    )

    def test_first_page_group_list_contains_ten_records(self):
        """Количество постов на первой странице group_list равно 10."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_contains_one_records(self):
        """Количество постов на второй странице group_list равно одному."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(
                reverse(
                    'posts:profile', kwargs={'username': self.author.username}
                )))
        profile_posts_list = response.context['page_obj']
        for post in profile_posts_list:
            with self.subTest(post=post):
                self.assertEqual(
                    post.author.username,
                    self.author.username,
                )

                # Добавлена проверка передачи картинки в контекст
                if post.id == self.additional_post_for_test.id:
                    self.assertEqual(
                        post.image,
                        self.additional_post_for_test.image,
                    )

    def test_first_page_profile_contains_ten_records(self):
        """Количество постов на первой странице profile равно 10."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_one_records(self):
        """Количество постов на второй странице profile равно двум."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(
                reverse(
                    'posts:post_detail', kwargs={
                        'post_id': self.additional_post_for_test.id
                    }
                )))

        post = response.context['post']
        self.assertEqual(post.group.title, self.group.title)
        self.assertEqual(post.text, self.additional_post_for_test.text)
        self.assertEqual(post.author.username, self.author.username)

        # Добавлена проверка передачи картинки в контекст
        if post.id == self.additional_post_for_test.id:
            self.assertEqual(post.image, self.additional_post_for_test.image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.additional_post_for_test.id},
            ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context_additional_post_with_group(self):
        """Шаблон index отображает пост с отдельной группой."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts_list = response.context['page_obj']
        for post in posts_list:
            if post.id == self.post_with_additional_group.id:
                additional_post = post

                post_group_0 = additional_post.group.title
                post_text_0 = additional_post.text
                post_author_0 = additional_post.author.username

                self.assertEqual(
                    post_group_0,
                    self.post_with_additional_group.group.title,
                )
                self.assertEqual(
                    post_text_0,
                    self.post_with_additional_group.text,
                )
                self.assertEqual(
                    post_author_0,
                    self.post_with_additional_group.author.username,
                )

    def test_group_list_page_show_correct_context_add_post_with_group(self):
        """Шаблон group_list отображает пост с отдельной группой."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.post_with_additional_group.group.slug
                }
            ))
        posts_list = response.context['page_obj']
        for post in posts_list:
            if post.id == self.post_with_additional_group.id:
                additional_post = post

                post_group_0 = additional_post.group.title
                post_text_0 = additional_post.text
                post_author_0 = additional_post.author.username

                self.assertEqual(
                    post_group_0,
                    self.post_with_additional_group.group.title,
                )
                self.assertEqual(
                    post_text_0,
                    self.post_with_additional_group.text,
                )
                self.assertEqual(
                    post_author_0,
                    self.post_with_additional_group.author.username,
                )

    def test_profile_page_show_correct_context_add_post_with_group(self):
        """Шаблон profile отображает пост с отдельной группой."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ))
        posts_list = response.context['page_obj']
        for post in posts_list:
            if post.id == self.post_with_additional_group.id:
                additional_post = post

                post_group_0 = additional_post.group.title
                post_text_0 = additional_post.text
                post_author_0 = additional_post.author.username

                self.assertEqual(
                    post_group_0,
                    self.post_with_additional_group.group.title,
                )
                self.assertEqual(
                    post_text_0,
                    self.post_with_additional_group.text,
                )
                self.assertEqual(
                    post_author_0,
                    self.post_with_additional_group.author.username,
                )

    def test_index_page_cache(self):
        """Информация на главной странице кэшируется 20 сек."""
        response = self.authorized_client.get(reverse('posts:index'))
        content = response.content

        post_for_delete = Post.objects.get(id=self.additional_post_for_test.id)
        post_for_delete.delete()

        response = self.authorized_client.get(reverse('posts:index'))
        content_cached = response.content

        self.assertEqual(content, content_cached)

        cache.clear()

        response = self.authorized_client.get(reverse('posts:index'))
        content_decached = response.content
        self.assertNotEqual(content_cached, content_decached)

    def test_authorized_user_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться
         на других пользователей и удалять их из подписок.
         """
        Follow.objects.all().delete()
        self.authorized_client_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username},
            ))
        self.assertTrue(
            self.user_follower.follower.filter(author=self.author).exists()
        )
        self.authorized_client_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username},
            ))
        self.assertFalse(
            self.user_follower.follower.filter(author=self.author).exists()
        )

    def test_new_post_show_follower_not_show_other(self):
        """Новая запись пользователя появляется в ленте тех,
         кто на него подписан и не появляется в ленте тех, кто не подписан.
         """
        # Подписчик получает список постов подписки
        self.authorized_client_follower.get(reverse('posts:follow_index'))
        follower_posts_list = self.user_follower.follower.filter(
            author=self.author
        ).count()
        # Не подписчик получает список постов подписки
        self.authorized_client_not_follower.get(reverse('posts:follow_index'))
        not_follower_posts_list = self.user_not_follower.follower.filter(
            author=self.author
        ).count()

        # Подписчик подписывается на автора
        self.authorized_client_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username},
            ))

        # Авто создает пост
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # Подписчик получает обновленный список постов подписки
        self.authorized_client_follower.get(reverse('posts:follow_index'))
        follower_posts_list_new = self.user_follower.follower.filter(
            author=self.author
        ).count()
        self.assertEqual(follower_posts_list + 1, follower_posts_list_new)
        # Не подписчик получает обновленный список постов подписки
        self.authorized_client_not_follower.get(
            reverse('posts:follow_index')
        )
        not_follower_posts_list_new = self.user_not_follower.follower.filter(
            author=self.author
        ).count()
        self.assertEqual(not_follower_posts_list, not_follower_posts_list_new)
