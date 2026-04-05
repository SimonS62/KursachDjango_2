from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    # Поле user только для чтения, чтобы показывать имя пользователя
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Habit
        fields = '__all__'
        # Поля, которые нельзя менять через API вручную
        read_only_fields = ('user', 'last_done', 'streak')

    def validate(self, data):
        """
        Вызываем валидацию clean() из модели Habit,
        чтобы бизнес-логика проверялась и в API.
        """
        # Создаем временный объект для проверки (не сохраняя в БД)
        instance = Habit(**data)
        instance.clean()
        return data

    def create(self, validated_data):
        # Привязываем привычку к текущему пользователю из запроса
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PublicHabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения только публичных привычек.
    """
    class Meta:
        model = Habit
        fields = [
            'id', 'action', 'time', 'place',
            'is_pleasant', 'periodicity', 'duration'
        ]
