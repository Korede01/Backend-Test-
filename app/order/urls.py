from django.urls import path, include
from .views import OrderViewSet



urlpatterns = [
    path('order/', OrderViewSet, name='order-detail'),
]
