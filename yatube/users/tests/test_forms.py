# from django.contrib.auth import get_user_model
# from django.test import TestCase, Client
# from django.urls import reverse
#
#
# User = get_user_model()
#
#
# class SignupFormTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#
#     def setUp(self):
#         self.guest_client = Client()
#
#     def test_guest_user_can_signup(self):
#         users_count = User.objects.count()
#         form_data = {
#             'first_name': 'Вася',
#             'last_name': 'Иванов',
#             'username': 'Vaso',
#             'email': 'book@book.ru',
#             'password1': '12345678z',
#             'password2': '12345678z',
#         }
#         response = self.guest_client.post(
#             reverse('users:signup'),
#             data=form_data,
#             follow=True
#         )
#
#         self.assertEqual(User.objects.count(), users_count + 1)
#         self.assertRedirects(response, reverse('posts:index'))
#         self.assertTrue(
#             User.objects.filter(
#                 first_name='Вася',
#                 last_name='Иванов',
#                 username='Vaso',
#                 email='book@book.ru',
#             ).exist()
#         )
#         self.assertEqual(response.status_code, 200)
