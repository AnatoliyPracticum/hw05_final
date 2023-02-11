from django.test import TestCase, Client, override_settings
from http import HTTPStatus
from posts.models import User


# class ViewTestClass(TestCase):
@override_settings(DEBUG=False)
class Custom404Template(TestCase):
    def test_error_page(self):
        """- Проверка обработки 404"""
        response = self.client.get('/nonexist-page/')
        # Проверьте, что статус ответа сервера - 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверьте, что используется шаблон core/404.html
        self.assertTemplateUsed(response, 'core/404.html')

    def test_custom_403csrf_template(self):
        """- Проверка обработки 403csrf"""
        user = User.objects.create_user(username='HasNoName')
        authorized_client = Client(enforce_csrf_checks=True)
        authorized_client.force_login(user)
        response = authorized_client.post('/create/')
        self.assertTemplateUsed(response, 'core/403csrf.html')
        # CSRF_FORM_URL = '/create/'
