from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus


class TestAbout(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url(self):
        urls_about = {
            "/about/author/": HTTPStatus.OK,
            "/about/tech/": HTTPStatus.OK,
        }
        for url, status_code in urls_about.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_about_template(self):
        templates = {
            "/about/author/": "about/author.html",
            "/about/tech/": "about/tech.html",
        }
        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_pages_templates(self):
        templates_pages = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        for template, url_names in templates_pages.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url_names)
                self.assertTemplateUsed(response, template)
