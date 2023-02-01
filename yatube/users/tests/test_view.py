# from django.contrib.auth import get_user_model
# from django.test import Client, TestCase
# from django.urls import reverse
# from http import HTTPStatus
#
#
# User = get_user_model()
#
#
# class StaticViewsTests(TestCase):
#     def setUp(self):
#         # Не авторизованный пользователь
#         self.guest_client = Client()
#         # Авторизованный пользователь
#         self.user = User.objects.create_user(username='auth')
#         self.authorized_client = Client()
#         self.authorized_client.force_login(self.user)
#
#     def test_user_signup_page_accessible(self):
#         """URL, генерируемый при помощи имени users:signup, доступен."""
#         response = self.guest_client.get(reverse('users:signup'))
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_login_page_accessible(self):
#         """URL, генерируемый при помощи имени users:login, доступен."""
#         response = self.guest_client.get(reverse('users:login'))
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_reset_page_accessible(self):
#         """URL, генерируемый при помощи имени users:password_reset,
#          доступен.
#          """
#         response = self.authorized_client.get(reverse(
#             'users:password_reset_form'
#         ))
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_reset_done_page_accessible(self):
#         """URL, генерируемый при помощи имени users:password_reset_done,
#          доступен.
#          """
#         response = self.authorized_client.get(reverse(
#             'users:password_reset_done'
#         ))
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_change_page_accessible(self):
#         """URL, генерируемый при помощи имени users:password_change,
#          доступен.
#          """
#         response = self.authorized_client.get(reverse(
#             'users:password_change_form'
#         ))
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_change_done_page_accessible(self):
#         """URL, генерируемый при помощи имени users:password_change_done,
#          доступен.
#          """
#         response = self.authorized_client.get(reverse(
#             'users:password_change_done'
#         ))
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_reset_complete_page_accessible(self):
#         """URL, генерируемый при помощи имени users:password_reset_complete,
#          доступен.
#          """
#         response = self.authorized_client.get(reverse(
#             'users:password_reset_complete'
#         ))
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     # Не получается передать uid и token
#     # def test_password_reset_confirm_page_accessible(self):
#     #     """URL, генерируемый при помощи имени users:password_reset_confirm,
#     #      доступен.
#     #      """
#     #     response = self.authorized_client.get(reverse(
#     #         'users:password_reset_confirm',
#     #         kwargs={'uidb64': '<uidb64>', 'token': 'token'},
#     #     ))
#     #     self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_logout_page_accessible(self):
#         """URL, генерируемый при помощи имени users:logout,
#          доступен.
#          """
#         response = self.authorized_client.get(reverse('users:logout'))
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_authorized_users_pages_uses_correct_template(self):
#         """При запросе авторизированных пользователей к приложению users
#         применяются правильные шаблоны."""
#         templates_users = {
#             'users:password_change_form': 'users/password_change_form.html',
#             'users:password_change_done': 'users/password_change_done.html',
#             'users:password_reset_form': 'users/password_reset_form.html',
#             'users:password_reset_done': 'users/password_reset_done.html',
#             'users:password_reset_complete':
#                 'users/password_reset_complete.html',
#             # reverse(
#             #     'users:password_reset_confirm',
#             #     kwargs={'uidb64': '<uidb64>', 'token': 'token'},
#             # ): 'users/password_reset_confirm.html',
#             'users:logout': 'users/logged_out.html',
#         }
#         for address, template in templates_users.items():
#             with self.subTest(address=address):
#                 response = self.authorized_client.get(reverse(address))
#                 self.assertTemplateUsed(response, template)
#
#     def test_guest_users_pages_uses_correct_template(self):
#         """При запросе не авторизованных пользователей к приложению users
#         применяются правильные шаблоны."""
#         templates_users = {
#             'users:signup': 'users/signup.html',
#             'users:login': 'users/login.html',
#         }
#         for address, template in templates_users.items():
#             with self.subTest(address=address):
#                 response = self.guest_client.get(reverse(address))
#                 self.assertTemplateUsed(response, template)
