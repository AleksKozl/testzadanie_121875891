"""
Wildberries Parser Celery Task

Содержит асинхронную задачу для парсинга товаров с Wildberries API.
PS: Можно было бы сделать через aiohttp внутри celery-задачи, но celery не поддерживает aiohttp напрямую,
    пришлось бы использовать "костыли" или другие сторонние модули, а это + время.

Функции:
    parse_wildberries(query): Основная задача парсинга

Особенности:
    - Парсит 5 страниц результатов (100+ товаров)
    - Использует случайные User-Agents для обхода блокировки
    - Добавляет рандомные задержки между запросами
    - Обновляет существующие и создает новые товары в БД
    - Обрабатывает конвертацию цен (копейки → рубли)
"""
import requests
from celery import shared_task
from django.utils import timezone
from products.models import Product
import time
import random
from fake_useragent import UserAgent


@shared_task
def parse_wildberries(query):
    """
    Основная задача парсинга Wildberries

    Параметры:
        query (str): Поисковый запрос (например: "ноутбуки")

    Логика работы:
        1. Формирует параметры запроса для Wildberries API
        2. Выполняет 5 запросов (по 1 на страницу) с задержками
        3. Обрабатывает каждый товар в ответе:
            - Конвертирует цены из копеек в рубли
            - Извлекает название, рейтинг, отзывы
        4. Разделяет товары на новые и существующие
        5. Пакетно создает/обновляет записи в базе данных

    Особенности реализации:
        - Пакетная обработка (bulk_create/bulk_update)
        - Фильтрация по wb_id для определения существующих товаров
        - Обновление только основных полей (price, rating и др.)
        - Защита от дубликатов через wb_id

    Возвращает:
        str: Статистика обработки ("Обработано: X | Новые: Y | Обновлены: Z")
        Или сообщение об ошибке при сбое

    Конфигурация запроса:
        - Регионы: Основные регионы РФ
        - Сортировка: по популярности (sort=popular)
        - Таймаут: 15 секунд на запрос
    """
    API_URL = "https://search.wb.ru/exactmatch/ru/common/v4/search"
    headers = {"User-Agent": UserAgent().random}
    scraped_products = []
    current_time = timezone.now()

    try:
        for page in range(1, 6):  # Парсим 5 страниц
            params = {
                "query": query,
                "page": page,
                "dest": -1257786,
                "regions": "80,64,83,4,38,33,70,82,69,68,86,30,40,48,1,22,66,31",
                "resultset": "catalog",
                "sort": "popular",
                "spp": 0,
                "appType": 1
            }

            response = requests.get(API_URL, headers=headers, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            if not data.get('data') or not data['data'].get('products'):
                break

            for product in data['data']['products']:
                try:
                    scraped_products.append({
                        "wb_id": product['id'],
                        "name": product['name'],
                        "price": product['priceU'] / 100,  # Конвертация из копеек
                        "discount_price": product.get('salePriceU', product['priceU']) / 100,
                        "rating": product.get('reviewRating'),
                        "reviews_count": product.get('feedbacks'),
                        "created_at": timezone.now()
                    })
                except Exception as e:
                    print(f"Ошибка обработки товара: {str(e)}")
            # Случайная задержка между запросами, чтобы не спамить
            time.sleep(random.uniform(1.5, 3.5))

        # Здесь решил добавить деление на уже существующие продукты и новые для обновления атрибутов
        wb_ids = [p["wb_id"] for p in scraped_products]
        existing_products = Product.objects.filter(wb_id__in=wb_ids).in_bulk(field_name="wb_id")

        to_create = []
        to_update = []

        for product in scraped_products:
            wb_id = product["wb_id"]

            if wb_id in existing_products:
                obj = existing_products[wb_id]
                obj.name = product["name"]
                obj.price = product["price"]
                obj.discount_price = product["discount_price"]
                obj.rating = product["rating"]
                obj.reviews_count = product["reviews_count"]
                to_update.append(obj)

            else:
                to_create.append(Product(
                    wb_id=wb_id,
                    name=product["name"],
                    price=product["price"],
                    discount_price=product["discount_price"],
                    rating=product["rating"],
                    reviews_count=product["reviews_count"],
                    created_at=current_time
                ))

        if to_create:
            Product.objects.bulk_create(to_create, batch_size=50)

        if to_update:
            fields = ["name", "price", "discount_price", "rating", "reviews_count"]
            Product.objects.bulk_update(to_update, fields, batch_size=50)

        return f"Обработано: {len(scraped_products)} | Новые: {len(to_create)} | Обновлены: {len(to_update)}"

    except Exception as e:
        return f"Ошибка парсинга: {str(e)}"
