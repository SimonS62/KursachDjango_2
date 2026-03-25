import serializers
from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Только для чтения, чтобы не показывать ID
    # related_habit = serializers.PrimaryKeyRelatedField(queryset=Habit.objects.filter(is_pleasant=True)) # Если хотите управлять через PKclass Meta:
    model = Habit
    fields = '__all__' # Или перечислите нужные поля
    read_only_fields = ('user', 'last_done', 'streak') # Поля, которые не должны редактироваться через API

def create(self, validated_data):
    # Связываем привычку с текущим пользователем
    validated_data['user'] = self.context['request'].user
    return super().create(validated_data)

# Переопределение create и update для валидации при сохранении
def validate(self, data):
    # Если вы хотите, чтобы валидаторы модели работали на уровне API,
    # можно вызвать instance.clean() здесь, но лучше использовать валидаторы DRF
    instance = Habit(**data) # Создаем временный экземпляр для clean()
    instance.clean() # Вызываем валидацию модели
    return data

def update(self, instance, validated_data):
    # Валидация при обновлении
    # instance.clean() # Проверим, является ли модифицированный экземпляр валидным
    return super().update(instance, validated_data)

    class PublicHabitSerializer(serializers.ModelSerializer):
        user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Habit
        fields = ('id', 'action', 'time', 'reward', 'is_pleasant', 'related_habit', 'is_public', 'user')
        read_only_fields = ('action', 'time', 'reward', 'is_pleasant', 'related_habit', 'is_public', 'user')