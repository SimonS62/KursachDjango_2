from celery import shared_task
from telegram import Bot
from telegram.error import TelegramError
from django.conf import settings
from habits.models import Habit
from telegram_bot.models import TelegramUser
from django.utils import timezone


bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

@shared_task
def send_habit_reminder(habit_id):
    """
    Отправляет напоминание о привычке пользователю Telegram.
    """
    # Инициализация бота внутри задачи для безопасности в Celery
    # Если bot = Bot(...) используется глобально, убедитесь, что настройки Django доступны
    # в процессе, где выполняется задача.
    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    except Exception as e:
        print(f"Error initializing Telegram bot: {e}")
        return # Не можем продолжить без бота

    try:
        # --- Внешний блок try для получения данных ---
        habit = Habit.objects.get(id=habit_id)
        telegram_user = TelegramUser.objects.filter(user=habit.user).first()

        # --- Проверка после получения данных ---
        if telegram_user:
            message = (
                f"Привет, {habit.user.username}! 👋\n"
                f"Не забудь про {habit.action} в {habit.time.strftime('%H:%M')} "
                f"в месте: '{habit.place}'.\n"
                f"Время на выполнение: {habit.execution_time_seconds} сек."
            )

            # --- Вложенный блок try для отправки сообщения ---
            try:
                bot.send_message(chat_id=telegram_user.chat_id, text=message)
                print(f"Reminder sent for habit {habit.id} to {telegram_user.chat_id}")
            except TelegramError as e:
                # Обработка ошибок отправки сообщения
                print(f"Error sending message for habit {habit.id} to {telegram_user.chat_id}: {e}")
            except Exception as e:
                # Обработка других неожиданных ошибок при отправке
                print(f"Unexpected error sending message for habit {habit.id} to {telegram_user.chat_id}: {e}")
        else:
            # Если TelegramUser не найден для данного пользователя привычки
            print(f"TelegramUser not found for habit {habit.id} (user_id={habit.user.id}). Cannot send reminder.")

    except Habit.DoesNotExist:
        # Обработка случая, когда привычка с указанным ID не найдена
        print(f"Habit with ID {habit_id} not found.")
    except Exception as e:
        # Обработка других неожиданных ошибок (например, проблемы с БД при получении Habit/TelegramUser)
        print(f"An unexpected error occurred while processing habit {habit_id}: {e}")

@shared_task
def schedule_reminders():
    now = timezone.localtime(timezone.now())