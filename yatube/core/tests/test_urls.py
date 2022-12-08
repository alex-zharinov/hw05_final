from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def test_404_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        self.guest_client = Client()
        response = self.guest_client.get('/unexisting_page/')
        template = 'core/404.html'
        self.assertTemplateUsed(response, template)
