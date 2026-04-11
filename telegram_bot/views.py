from django.views import View
from django.http import JsonResponse
import json
import logging


logger = logging.getLogger(__name__)

class TelegramWebhookView(View):
    """
    Обработчик вебхуков от Telegram.
    """

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        """
        Принимает обновления от Telegram.
        """
        try:
            # Получаем данные от Telegram
            update = json.loads(request.body)
            logger.info(f"Получено обновление от Telegram: {update}")

            # Здесь должна быть логика обработки сообщений
            # Например, обработка команд, текстовых сообщений и т.д.

            # Пока просто возвращаем успешный ответ
            return JsonResponse({'status': 'ok'})

        except json.JSONDecodeError:
            logger.error("Неверный JSON в теле запроса")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Ошибка при обработке вебхука: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
