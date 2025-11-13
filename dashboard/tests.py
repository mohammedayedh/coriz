from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardViewsSmokeTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='strong-pass-123',
            is_verified=True,
        )

    def _get(self, name, **kwargs):
        self.client.force_login(self.user)
        url = reverse(name, kwargs=kwargs) if kwargs else reverse(name)
        return self.client.get(url)

    def test_dashboard_index(self):
        response = self._get('dashboard:index')
        self.assertEqual(response.status_code, 200)

    def test_posts_management(self):
        response = self._get('dashboard:posts_management')
        self.assertEqual(response.status_code, 200)

    def test_notifications_requires_login(self):
        response = self._get('dashboard:notifications')
        self.assertEqual(response.status_code, 200)
