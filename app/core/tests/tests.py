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
        self.user = User.objects.create_user(username='testuser', email='example@gmail.com', password='testpassword')
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
        """
        Ensure we can retrieve all products.
        """
        url = reverse('product-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_product_detail(self):
        """
        Ensure we can retrieve a product by its ID.
        """
        url = reverse('product-detail', args=[self.product1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')

    def test_create_product_authenticated(self):
        """
        Ensure we can create a new product when authenticated.
        """
        url = reverse('product-list-create')
        data = {
            'name': 'Keyboard',
            'description': 'Mechanical keyboard for gaming',
            'price': 100.00,
            'stock': 20,
            'category': self.category1.id
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_create_product_unauthenticated(self):
        """
        Ensure we cannot create a product when unauthenticated.
        """
        url = reverse('product-list-create')
        data = {
            'name': 'Mouse',
            'description': 'Wireless mouse',
            'price': 50.00,
            'stock': 30,
            'category': self.category1.id
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_authenticated(self):
        """
        Ensure we can update an existing product when authenticated.
        """
        url = reverse('product-detail', args=[self.product1.id])
        data = {
            'name': 'Laptop Pro',
            'description': 'Upgraded powerful laptop for professionals',
            'price': 2000.00,
            'stock': 5,
            'category': self.category1.id
        }

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, 'Laptop Pro')
        self.assertEqual(self.product1.price, 2000.00)

    def test_delete_product_authenticated(self):
        """
        Ensure we can delete an existing product when authenticated.
        """
        url = reverse('product-detail', args=[self.product1.id])

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)

    def test_search_products(self):
        """
        Ensure we can search for products.
        """
        url = reverse('product-list-create') + '?search=Laptop'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_pagination(self):
        """
        Ensure the product list endpoint supports pagination.
        """
        url = reverse('product-list-create') + '?page=1&page_size=1'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('next', response.data)

    def test_filter_products_by_category(self):
        """
        Ensure we can filter products by category.
        """
        url = reverse('product-list-create') + f'?category={self.category1.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop')

    def test_sort_products_by_price(self):
        """
        Ensure we can sort products by price.
        """
        url = reverse('product-list-create') + '?ordering=price'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'T-shirt')
