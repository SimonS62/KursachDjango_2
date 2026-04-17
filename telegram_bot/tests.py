from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TelegramBotTests(APITestCase):

    def setUp(self):
        """Настройка тестового окружения."""
        # Предположим, что в telegram_bot/urls.py есть 'telegram-webhook'
        self.webhook_url = reverse('telegram-webhook')


    def test_telegram_webhook_message_received(self):
        """Тестирование получения сообщения от Telegram."""
        # Пример структуры входящего сообщения от Telegram API
        # Это сильно зависит от вашего обработчика
        telegram_message = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 111111111, "is_bot": False, "first_name": "TestUser"},
                "chat": {"id": 111111111, "first_name": "TestUser", "type": "private"},
                "date": 1678886400,
                "text": "/start" # Пример текста сообщения
            }
        }
        response = self.client.post(self.webhook_url, telegram_message, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Здесь можно добавить проверки, что произошло после получения сообщения,
        # например, создание пользователя, отправка ответа и т.д.
        # self.assertEqual(User.objects.count(), 1)
        # self.assertEqual(response.data.get('text'), 'Добро пожаловать!') # Если API возвращает ответ

    def test_telegram_webhook_other_type(self):
        """Тестирование получения другого типа обновления (например, callback query)."""
        # Пример другой структуры
        telegram_callback = {
            "update_id": 987654321,
            "callback_query": {
                "id": "12345",
                "from": {"id": 111111111, "is_bot": False, "first_name": "TestUser"},
                "message": {
                    "message_id": 10,
                    "chat": {"id": 111111111, "first_name": "TestUser", "type": "private"},
                    "date": 1678886400,
                    "text": "Какое-то сообщение"
                },
                "chat_instance": "111111111",
                "data": "some_callback_data"
            }
        }
        response = self.client.post(self.webhook_url, telegram_callback, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)