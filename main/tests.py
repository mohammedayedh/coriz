from django.test import TestCase
from django.urls import reverse


class MainViewsSmokeTests(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)

    def test_posts_list_page(self):
        response = self.client.get(reverse('main:posts_list'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('main:about'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get(reverse('main:contact'))
        self.assertEqual(response.status_code, 200)
