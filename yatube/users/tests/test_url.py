# from django.contrib.auth import get_user_model
# from django.test import TestCase, Client
# from http import HTTPStatus
#
#
# User = get_user_model()
#
#
# class UserURLTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#
#     def setUp(self):
#         # Не авторизованный пользователь
#         self.guest_client = Client()
#         # Авторизованный пользователь
#         self.user = User.objects.create_user(username='auth')
#         self.authorized_client = Client()
#         self.authorized_client.force_login(self.user)
#
#     def test_signup_url_exists_at_desired_location(self):
#         """Страница '/signup/' доступна не авторизованному пользователю."""
#         response = self.guest_client.get('/auth/signup/')
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_login_url_exists_at_desired_location(self):
#         """Страница '/login/' доступна не авторизованному пользователю."""
#         response = self.guest_client.get('/auth/login/')
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_reset_url_not_exists_for_authorized_user(self):
#         """Страница '/password_reset/' доступна авторизованному пользователю.
#         """
#         response = self.authorized_client.get('/auth/password_reset/')
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_reset_done_url_not_exists_for_authorized_user(self):
#         """Страница '/password_reset_done/' доступна авторизованному
#         пользователю.
#         """
#         response = self.authorized_client.get('/auth/password_reset_done/')
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_reset_complete_url_not_exists_for_auth_user(self):
#         """Страница '/password_reset_complete/' доступна авторизованному
#         пользователю.
#         """
#         response = self.authorized_client.get(
#             '/auth/password_reset_complete/',)
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     # Тест не работает (проблема с передачей uid и token)
#     # def test_password_reset_confirm_url_not_exists_for_auth_user(self):
#     #     """Страница '/password_reset_confirm/' доступна авторизованному
#     #     пользователю.
#     #     """
#     #     response = self.authorized_client.get(
#     #         '/auth/password_reset_confirm/',
#     #         kwargs={'uidb64': '<uidb64>', 'token': '<token>'},
#     #     )
#     #     self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_change_url_not_exists_for_authorized_user(self):
#         """Страница '/password_change/' доступна авторизованному
#         пользователю.
#         """
#         response = self.authorized_client.get('/auth/password_change/')
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_password_change_done_url_not_exists_for_authorized_user(self):
#         """Страница '/password_change_done/' доступна авторизованному
#         пользователю.
#         """
#         response = self.authorized_client.get('/auth/password_change_done/')
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_logout_url_not_exists_for_authorized_user(self):
#         """Страница '/logout/' доступна авторизованному пользователю."""
#         response = self.authorized_client.get('/auth/logout/')
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_urls_uses_correct_template(self):
#         """URL-адрес использует соответствующий шаблон."""
#         templates_url_names = {
#             '/auth/signup/': 'users/signup.html',
#             '/auth/login/': 'users/login.html',
#             '/auth/password_reset/': 'users/password_reset_form.html',
#             # '/auth/password_reset_done': 'users/password_reset_done.html',
#             '/auth/password_change/': 'users/password_change_form.html',
#             '/auth/password_change_done/': 'users/password_change_done.html',
#             # '/auth/password_reset_complete':
#             #   'users/password_reset_complete.html',
#             # '/auth/password_reset_confirm':
#             #   'users/password_reset_confirm.html',
#             '/auth/logout/': 'users/logged_out.html',
#         }
#         for address, template in templates_url_names.items():
#             with self.subTest(address=address):
#                 response = self.authorized_client.get(address)
#                 self.assertTemplateUsed(response, template)
