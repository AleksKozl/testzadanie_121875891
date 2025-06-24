from django.urls import path
from .views import ParseProductsView

urlpatterns = [
    path('parse/', ParseProductsView.as_view(), name='parse-products'),
]