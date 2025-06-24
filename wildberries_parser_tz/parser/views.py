"""
Wildberries Parser API View

Предоставляет эндпоинт для запуска парсинга товаров с Wildberries.

Классы:
    ParseProductsView: Обработчик POST-запросов для инициализации парсинга.

Пример запроса:
    POST /parse/
    {
        "query": "ноутбуки"
    }

Ответ:
    202 Accepted: {
        "status": "Парсинг запущен",
        "task_id": "celery-task-id-123"
    }
    400 Bad Request: {"error": "Параметр 'query' обязателен"}
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from parser.celery_tasks.parser_tasks import parse_wildberries
from rest_framework.permissions import AllowAny


class ParseProductsView(APIView):
    """
    API View для запуска парсинга Wildberries

    Параметры:
        permission_classes: Разрешает доступ без аутентификации (AllowAny)

    Методы:
        post(request): Обрабатывает POST-запрос для запуска парсинга

    Логика работы:
        1. Проверяет наличие обязательного параметра 'query'
        2. Запускает Celery-задачу parse_wildberries с переданным запросом
        3. Возвращает ID задачи и статус 202 (Accepted)

    Особенности:
        - Асинхронная обработка через Celery
        - Возвращает идентификатор задачи для отслеживания статуса
        - Логирует ID задачи в консоль (для дебага)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response(
                {"error": "Параметр 'query' обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        task = parse_wildberries.delay(query)
        print(task, flush=True)
        return Response(
            {
                "status": "Парсинг запущен",
                "task_id": task.id
            },
            status=status.HTTP_202_ACCEPTED
        )
