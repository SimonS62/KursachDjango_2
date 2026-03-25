from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
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
    pagination_class = HabitPagination  # Применяем пагинациюdef get_queryset(self):
    # Для GET запросов к списку, возвращаем только привычки текущего пользователя
    if self.action == 'list':
        return Habit.objects.filter(user=self.request.user).order_by('id')
    # Для других действий (retrieve, update, destroy) возвращаем конкретный объект,
    # а Django REST Framework сам проверит права доступа.
    return Habit.objects.all()


def perform_create(self, serializer):
    # При создании, автоматически присваиваем текущего пользователя
    serializer.save(user=self.request.user)


@action(detail=True, methods=['post'])
def mark_done(self, request, pk=None):
    habit = self.get_object()
    # Логика отметки привычки как выполненной
    # Здесь можно обновлять last_done, streak, и, возможно, управлять связанной приятной привычкой
    # ...
    return Response({'status': 'habit marked as done'})


@action(detail=False, permission_classes=[permissions.AllowAny])  # Публичные привычки доступны всем
def public(self, request):
    queryset = Habit.objects.filter(is_public=True)
    page = self.paginate_queryset(queryset)
    if page is not None:
        serializer = PublicHabitSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    serializer = PublicHabitSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)


