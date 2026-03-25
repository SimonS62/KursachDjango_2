from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError


class Habit(models.Model):
    DoesNotExist = None
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    action = models.CharField(max_length=255, verbose_name="Действие") # Пример verbose_name
    time = models.TimeField(verbose_name="Время") # Пример verbose_name

    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='related_habits',
        null=True,
        blank=True,
        verbose_name="Связанная привычка" # Пример verbose_name
    )
    periodicity_days = models.PositiveIntegerField(verbose_name="Дней периодичности") # Например, 1 (ежедневно), 7 (еженедельно)
    execution_time_seconds = models.PositiveIntegerField(verbose_name="Время на выполнение (сек)") # Время на выполнение привычки в секундах
    is_public = models.BooleanField(default=False, verbose_name="Публичная") # Видимость привычки
    last_done = models.DateTimeField(null=True, blank=True, verbose_name="Последнее выполнение") # Кагда была выполнена в последний раз
    streak = models.PositiveIntegerField(default=0, verbose_name="Серия") # Текущая серия выполнения

    class Meta:
        # Пример дополнительных настроек метаданных
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ['time'] # Пример сортировки

    def __str__(self):
        """
        Возвращает строковое представление объекта Habit.
        """
        return f'{self.action} в {self.time.strftime("%H:%M")}' # Более красивое форматирование времени

    def clean(self):
        """
        Метод для дополнительной валидации полей модели.
        """
        # Эта проверка может быть на строке 70 в вашем коде, если здесь используется 'self'
        if self.related_habit and self.related_habit == self:
             raise ValidationError("Связанная привычка не может быть самой собой.")

        if self.execution_time_seconds > 120:
            raise ValidationError(
                "Время выполнения должно быть не более 120 секунд."
            )

        # Пример другой валидации:
        # if self.user and self.is_public and self.related_habit:
        #     raise ValidationError("Публичные привычки не могут иметь связанных привычек.")

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для выполнения валидации перед сохранением.
        """
        # Вызов self.clean() перед сохранением, чтобы проверить данные
        self.clean()