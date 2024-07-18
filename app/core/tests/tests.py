from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Product, Category
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

class ProductAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create a user (for testing authentication)
        self.user = User.objects.create_user(name='testuser', email='example@gmail.com', password='testpassword')
        self.access_token = AccessToken.for_user(self.user)

        # Create categories
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Clothing')

        # Create products
        self.product1 = Product.objects.create(
            name='Laptop',
            description='Powerful laptop for professionals',
            price=1500.00,
            stock=10,
            category=self.category1
        )
        self.product2 = Product.objects.create(
            name='T-shirt',
            description='Comfortable cotton t-shirt',
            price=20.00,
            stock=50,
            category=self.category2
        )

    def test_get_all_products(self):
        # Test retrieving all products
        url = reverse('product-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Assuming you have 2 products in setUp

    def test_get_product_detail(self):
        # Test retrieving a single product detail
        url = reverse('product-detail', args=[self.product1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')

    def test_create_product_authenticated(self):
        # Test creating a product when authenticated
        url = reverse('product-list-create')
        data = {
            'name': 'Keyboard',
            'description': 'Mechanical keyboard for gaming',
            'price': 100.00,
            'stock': 20,
            'category': self.category1.id  # Assuming category ID is sent in the request
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)  # Assuming new product is created

    # Add more tests for update, delete, search functionality, etc.

    # Example of test for search functionality
    def test_search_products(self):
        # Test searching for products
        url = reverse('product-list-create') + '?search=Laptop'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Assuming only one product matches 'Laptop'

    # Example of test for pagination
    def test_pagination(self):
        # Test pagination of products
        url = reverse('product-list-create') + '?page=1&page_size=1'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('next', response.data)  # Check if 'next' pagination link is present

