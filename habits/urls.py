from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    # Добавляем эндпоинт для публичных привычек
    path('habits/public/', HabitViewSet.as_view({'get': 'public'}), name='habit-public-list'),
]
