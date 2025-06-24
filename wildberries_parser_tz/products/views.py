from rest_framework import generics

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Max

from products.models import Product
from products.filters import ProductFilter
from products.serializers import ProductSerializer


class ProductListView(generics.ListAPIView):
    """
    API endpoint для получения списка товаров с возможностью фильтрации и сортировки.
    Поддерживаемые параметры:
    - min_price: Минимальная цена товара
    - max_price: Максимальная цена товара
    - min_rating: Минимальный рейтинг товара
    - min_reviews: Минимальное количество отзывов
    - ordering: Поле для сортировки (price, rating, reviews_count, created_at)
    Примеры запросов:
    GET /api/products/?min_price=100&max_price=1000&min_rating=4&ordering=-price
    GET /api/products/?min_reviews=10&page=2
    """
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    ordering_fields = ["price", "rating", "reviews_count", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        ordering = self.request.query_params.get('ordering')
        if ordering:
            return queryset.order_by(ordering)
        return queryset


class HomeView(TemplateView):
    """
    Главная страница аналитической панели Wildberries.
    Отображает:
    - Таблицу товаров с фильтрацией
    - График распределения цен
    - График зависимости скидок от рейтинга
    - Панель фильтров
    """
    template_name = 'products/index.html'


def max_price(request):
    """
    Возвращает максимальную цену среди всех товаров в формате JSON.
    Пример ответа:
    {"max_price": 9999.99}
    """
    max_price = Product.objects.aggregate(max_price=Max('price'))['max_price'] or 0
    return JsonResponse({'max_price': max_price})
