from http import HTTPStatus as ht
from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, ht.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
