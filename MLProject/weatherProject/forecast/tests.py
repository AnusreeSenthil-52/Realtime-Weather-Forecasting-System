from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from dotenv import load_dotenv


class WeatherDataTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        load_dotenv()

    def test_weather_page_loads(self):
        url = reverse('weather_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
