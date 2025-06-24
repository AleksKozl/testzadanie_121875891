from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from products.models import Product


class ProductAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        Product.objects.create(name='Product 1', price=100.0, discount_price=90.0, rating=4.5, reviews_count=10, wb_id=1)
        Product.objects.create(name='Product 2', price=200.0, discount_price=180.0, rating=4.0, reviews_count=20, wb_id=2)
        Product.objects.create(name='Product 3', price=300.0, discount_price=270.0, rating=3.5, reviews_count=30, wb_id=3)

    def test_get_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_filter_by_min_price(self):
        url = reverse('product-list')
        response = self.client.get(url, {'min_price': 150})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_max_price(self):
        url = reverse('product-list')
        response = self.client.get(url, {'max_price': 250})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_min_rating(self):
        url = reverse('product-list')
        response = self.client.get(url, {'min_rating': 4.0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_min_reviews(self):
        url = reverse('product-list')
        response = self.client.get(url, {'min_reviews': 15})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_ordering_by_price_asc(self):
        url = reverse('product-list')
        response = self.client.get(url, {'ordering': 'price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [item['price'] for item in response.data['results']]
        self.assertEqual(prices, ['100.00', '200.00', '300.00'])

    def test_ordering_by_price_desc(self):
        url = reverse('product-list')
        response = self.client.get(url, {'ordering': '-price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [item['price'] for item in response.data['results']]
        self.assertEqual(prices, ['300.00', '200.00', '100.00'])

    def test_max_price_endpoint(self):
        url = reverse('max_price')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'max_price': '300'})
