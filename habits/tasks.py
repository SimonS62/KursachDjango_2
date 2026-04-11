from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from telegram import Bot
from telegram.error import TelegramError
from habit_tracker import settings
from .models import Habit
import logging


logger = logging.getLogger(__name__)
User = get_user_model()

# Инициализация бота. Лучше делать это здесь, чтобы избежать повторных инициализаций
# при каждом вызове задачи, но убедитесь, что settings.py доступен.
try:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
except Exception as e:
    logger.error(f"Не удалось инициализировать Telegram Bot: {e}. Убедитесь, что TELEGRAM_BOT_TOKEN установлен в settings.py.")
    bot = None # Устанавливаем в None, чтобы задачи с Telegram не падали, если токен не задан


def send_tg_message(user_id: int, text: str):
    """Вспомогательная функция для отправки сообщения в Telegram."""
    if bot:
        try:
            bot.send_message(chat_id=user_id, text=text)
            logger.info(f"Сообщение отправлено пользователю {user_id}: {text[:50]}...")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
            return False
    else:
        logger.warning(f"Telegram Bot не инициализирован. Невозможно отправить сообщение пользователю {user_id}.")
        return False

@shared_task
def send_habit_reminder():
    """
    Задача для отправки напоминаний о привычках.
    Проверяет привычки, у которых время выполнения наступило,
    и отправляет уведомления пользователям.
    """
    try:
        now = timezone.now()
        current_time = now.time()
        current_date = now.date()

        # Находим привычки, которые должны быть выполнены сейчас
        habits = Habit.objects.filter(
            time__hour=current_time.hour,
            time__minute=current_time.minute,
            is_pleasant=False  # Только полезные привычки (или можно убрать фильтр)
        ).select_related('user')

        count = 0
        for habit in habits:
            # Проверяем, не была ли привычка уже выполнена сегодня
            # (если у вас есть поле last_completed в модели Habit)
            if hasattr(habit, 'last_completed'):
                if habit.last_completed == current_date:
                    continue

            # Здесь должна быть логика отправки уведомления
            # Например, через Telegram бота
            logger.info(f"Отправка напоминания: {habit.user.username} - {habit.action}")

            # Временный вывод в консоль для тестирования
            print(f"[{now}] Напоминание для {habit.user.username}: {habit.action}")

            # Если у привычки есть связанная приятная привычка
            if habit.related_habit:
                print(f"    После этого можно: {habit.related_habit.action}")

            # Если есть вознаграждение
            if habit.reward:
                print(f"    Вознаграждение: {habit.reward}")

            count += 1

        logger.info(f"Отправлено {count} напоминаний")
        return f"Successfully sent {count} reminders"

    except Exception as e:
        logger.error(f"Ошибка при отправке напоминаний: {str(e)}", exc_info=True)
        raise


@shared_task
def test_task():
    """
    Тестовая задача для проверки работы Celery.
    """
    print("Тестовая задача Celery выполнена!")
    return "Test task completed"
