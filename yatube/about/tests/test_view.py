from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:author, доступен."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:tech, доступен."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_pages_uses_correct_template(self):
        """При запросе к приложению about
        применяется шаблон 'about/...html'."""
        templates_about = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for address, template in templates_about.items():
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(address))
                self.assertTemplateUsed(response, template)
