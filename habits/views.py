from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer


# Пагинация
class HabitPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HabitPagination

    def get_queryset(self):
        """
        Определяет набор объектов, которые могут быть доступны для данной
        операции.
        """
        user = self.request.user
        if self.action == 'list':
            # Для списка (GET /habits/) возвращаем только привычки текущего пользователя
            return Habit.objects.filter(user=user).order_by('id')
        else:
            # Для остальных действий (retrieve, update, destroy, partial_update):
            # возвращаем только привычки текущего пользователя.
            # Таким образом, даже если объект существует, пользователь сможет
            # получить/изменить/удалить только свои.
            # DRF сам проверит, что запрашиваемый pk принадлежит пользователю.
            return Habit.objects.filter(user=user)

    def perform_create(self, serializer):
        # При создании, автоматически присваиваем текущего пользователя
        serializer.save(user=self.request.user)


    @action(detail=True, methods=['post'])
    def mark_done(self):
        # self.get_object() уже получает объект Habit, отфильтрованный по текущему пользователю
        habit = self.get_object() # <-- habit теперь используется

        # Логика отметки привычки как выполненной
        # Например, обновление поля last_done, или счетчика streak
        # Для примера, просто обновим 'last_done' на текущую дату (или время)
        # Если у вас есть поле last_done в модели Habit:
        try:
            # Импортируйте datetime, если еще не сделали этого в начале файла:
            # from datetime import datetime
            from django.utils import timezone # Лучше использовать timezone для работы с датами в Django

            habit.last_done = timezone.now() # Обновляем дату последнего выполнения
            # Если у вас есть поле streak, вы можете его увеличить:
            # habit.streak += 1
            habit.save()
            return Response({'status': 'habit marked as done', 'habit_id': habit.id})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


    @action(detail=False, permission_classes=[permissions.AllowAny])
    def public(self, request): # <-- request теперь используется
        queryset = Habit.objects.filter(is_public=True)
        page = self.paginate_queryset(queryset)

        if page is not None:
            # context={'request': request} является хорошей практикой,
            # если сериализатор может использовать request (например, для генерации URL)
            serializer = PublicHabitSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        # Если пагинация не используется (что маловероятно с PageNumberPagination,
        # но допустимо, если page_size=None или таких запросов нет)
        serializer = PublicHabitSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


