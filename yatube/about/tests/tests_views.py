from django.test import Client, TestCase
from django.urls import reverse


class StaticTemplateTests(TestCase):
    def setUp(self):
        self.unauthorised_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-adresses tech and author use correct HTML-templates."""
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.unauthorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
