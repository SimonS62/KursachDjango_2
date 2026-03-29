from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    action = models.CharField(max_length=255, verbose_name="Действие")
    place = models.CharField(max_length=255, verbose_name="Место", default="Дом")  # Добавлено
    time = models.TimeField(verbose_name="Время")
    is_pleasant = models.BooleanField(default=False, verbose_name="Приятная привычка")  # Добавлено

    related_habit = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='related_habits', verbose_name="Связанная привычка"
    )
    periodicity_days = models.PositiveIntegerField(default=1, verbose_name="Дней периодичности")
    execution_time_seconds = models.PositiveIntegerField(verbose_name="Время на выполнение (сек)")
    is_public = models.BooleanField(default=False, verbose_name="Публичная")
    last_done = models.DateTimeField(null=True, blank=True)
    streak = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ['time']

    def __str__(self):
        return f'{self.action} в {self.time}'

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