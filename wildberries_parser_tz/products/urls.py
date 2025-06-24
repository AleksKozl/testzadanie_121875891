from django.urls import path
from products.views import ProductListView, max_price

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('max_price/', max_price, name='max_price'),
]
