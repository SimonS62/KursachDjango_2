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
    reward = models.CharField(max_length=255, null=True, blank=True)
    last_completed = models.DateField(null=True, blank=True)
    periodicity_days = models.PositiveIntegerField(default=1, verbose_name="Дней периодичности")
    execution_time_seconds = models.PositiveIntegerField(verbose_name="Время на выполнение (сек)")
    is_public = models.BooleanField(default=False, verbose_name="Публичная")
    last_done = models.DateTimeField(null=True, blank=True)
    streak = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ['time']

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.associated_habit = None
        self.periodicity = None

    def __str__(self):
        return f'{self.action} в {self.time}'

    def clean(self):
        super().clean()
        # Валидируем время выполнения (не более 120 секунд)
        if self.time and self.time.total_seconds() > 120:
            raise ValidationError('Время выполнения привычки не может превышать 120 секунд.')
    
        # Валидируем периодичность (от 1 до 7 дней)
        if self.periodicity is not None and not (1 <= self.periodicity <= 7):
            raise ValidationError('Периодичность должна быть от 1 до 7 дней.')
    
        # Валидируем, что связанная привычка не является текущей (если она есть)
        if self.associated_habit and self.associated_habit == self:
             raise ValidationError('Связанная привычка не может быть самой собой.')


    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для выполнения валидации перед сохранением.
        """
        # Вызов self.clean() перед сохранением, чтобы проверить данные
        self.clean()