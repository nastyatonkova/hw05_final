from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.unauthorised_client = Client()

    def test_about_author_and_tech_accessible(self):
        """URL about:author and tech are accessible."""
        page_url_names = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for page, expected_status in page_url_names.items():
            with self.subTest(page=page):
                response = self.unauthorised_client.get(page).status_code
                self.assertEqual(response, expected_status)
