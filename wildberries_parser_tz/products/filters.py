import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Фильтр для товаров Wildberries.
    Поддерживаемые фильтры:
    - min_price: Фильтрация по минимальной цене (>=)
    - max_price: Фильтрация по максимальной цене (<=)
    - min_rating: Фильтрация по минимальному рейтингу (>=)
    - min_reviews: Фильтрация по минимальному количеству отзывов (>=)
    """

    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    min_reviews = django_filters.NumberFilter(field_name="reviews_count", lookup_expr="gte")

    class Meta:
        model = Product
        fields = []
