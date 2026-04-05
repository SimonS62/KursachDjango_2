from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


User = get_user_model()


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    action = models.CharField(max_length=255, verbose_name="Действие")
    place = models.CharField(max_length=255, verbose_name="Место", default="Дом")
    time = models.TimeField(verbose_name="Время")
    is_pleasant = models.BooleanField(default=False, verbose_name="Приятная привычка")

    related_habit = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='related_habits', verbose_name="Связанная привычка")
    reward = models.CharField(max_length=255, null=True, blank=True, verbose_name="Вознаграждение")
    last_completed = models.DateField(null=True, blank=True)
    periodicity = models.PositiveSmallIntegerField(default=1)
    execution_time_seconds = models.PositiveIntegerField(verbose_name="Время на выполнение (сек)")
    is_public = models.BooleanField(default=False, verbose_name="Публичная")
    last_done = models.DateTimeField(null=True, blank=True)
    streak = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ['time']

    def __str__(self):
        return f'{self.action} ({self.get_periodicity_display()})' if self.periodicity != 1 else f'{self.action}'

    def clean(self):
        super().clean()
        # 1. Время выполнения должно быть не больше 120 секунд.
        if self.execution_time_seconds is not None and self.execution_time_seconds > 120:
            raise ValidationError({'execution_time_seconds': 'Время выполнения привычки не может превышать 120 секунд.'})
        if self.execution_time_seconds is not None and self.execution_time_seconds <= 0:
             raise ValidationError({'execution_time_seconds': 'Время выполнения привычки должно быть больше 0 секунд.'})

        # 2. Периодичность: не реже 1 раза в 7 дней => periodicity <= 7
        if self.periodicity is not None:
            if not (1 <= self.periodicity <= 7):
                raise ValidationError({'periodicity': 'Периодичность не может быть реже, чем 1 раз в 7 дней (максимум 7 дней).'})

        # 3. Исключить одновременный выбор связанной привычки и вознаграждения.
        #    А также: у приятной привычки не может быть вознаграждения или связанной привычки.
        if self.is_pleasant:
            # Если привычка приятная, она не должна иметь ни вознаграждения, ни связанной привычки.
            if self.reward:
                raise ValidationError({'reward': 'Приятные привычки не могут иметь вознаграждения.'})
            if self.related_habit:
                raise ValidationError({'related_habit': 'Приятные привычки не могут быть связаны с другими привычками.'})
        else:
            # Если привычка НЕ приятная, можно иметь либо вознаграждение, либо связанную привычку, но не оба.
            if self.reward and self.related_habit:
                # Показываем ошибку на более общее поле, или можем показать на оба
                raise ValidationError({'reward': 'Нельзя одновременно указать вознаграждение и связанную привычку.'})

        if self.related_habit and hasattr(self.related_habit, 'is_pleasant'):
            if not self.related_habit.is_pleasant:
                raise ValidationError({'related_habit': 'Связанная привычка должна быть приятной привычкой.'})
