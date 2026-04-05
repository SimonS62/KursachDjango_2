from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from habits.models import Habit
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


class HabitTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')

        # 2. Создаем клиент для второго пользователя
        self.client_user2 = APIClient()

        # 3. Авторизуем второй клиент
        self.client_user2.force_authenticate(user=self.user2)

        # Создаем привычки напрямую через Habit.objects.create
        # Убедитесь, что имена полей (owner, action и т.д.) совпадают с вашей моделью
        self.habit1 = Habit.objects.create(
            user=self.user1,
            action='Утренняя зарядка',
            time='08:00:00',
            execution_time_seconds=60,
            periodicity=1,
        )

        self.habit2 = Habit.objects.create(
            user=self.user1,
            action='Читать 30 минут',
            place='Кровать',
            time='21:00:00',
            execution_time_seconds=120,
            periodicity=1,
            is_public=True,
            is_pleasant=False
        )

        self.habit3 = Habit.objects.create(
            user=self.user2,
            action='Медитация',
            place='Зал',
            time='12:00:00',
            execution_time_seconds=30,
            periodicity=1,
            is_public=False,
            is_pleasant=True
        )

        self.client.force_authenticate(user=self.user1)

        # URL-адреса для тестов
        self.list_url = reverse('habit-list')
        self.detail_url = lambda habit_id: reverse('habit-detail', kwargs={'pk': habit_id})
        self.log_create_url = lambda habit_id: reverse('habit-log-create', kwargs={'habit_id': habit_id})
        self.public_list_url = reverse('habit-public-list')

    def test_initial_habit_data_setup(self):
        """Тестирование создания новой привычки."""
        self.assertEqual(Habit.objects.count(), 3)
        self.assertEqual(self.habit1.user, self.user1)
        self.assertEqual(self.habit1.action, 'Утренняя зарядка')

    def test_habit_list_own(self):
        """Тестирование получения списка своих привычек."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2, f"Expected 2 habits in response data, got {len(response.data)}")

    def test_habit_list_other_user_habits_hidden(self):
        """Тестирование, что пользователь не видит чужие приватные привычки."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habits_in_response = response.data.get('results', response.data)
        user1_habit_ids = [h['id'] for h in habits_in_response]

        # Привычка user2 (private) не должна быть в списке user1
        self.assertNotIn(self.habit3.id, user1_habit_ids, "User1 should not see User2's private habit.")

        # Дополнительная проверка: User1 видит свои привычки
        self.assertIn(self.habit1.id, user1_habit_ids, "User1 should see their own private habit.")
        self.assertIn(self.habit2.id, user1_habit_ids, "User1 should see their own public habit.")

    def test_habit_retrieve_detail(self):
        """Тестирование получения деталей одной привычки."""
        url = self.detail_url(self.habit1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'Утренняя зарядка')

    def test_habit_retrieve_detail_forbidden_other_user(self):
        """Тестирование попытки получить детали чужой приватной привычки."""
        url = self.detail_url(self.habit3.id)  # Привычка user2
        response = self.client.get(url)
        # Обычно возвращается 403 Forbidden или 404 Not Found
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_habit_retrieve_detail_public_other_user(self):
        """Тестирование получения деталей чужой публичной привычки."""
        url = self.detail_url(self.habit2.id)
        response = self.client_user2.get(url)

        # Проверяем, что запрос прошел успешно (200 OK)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что в ответе пришло верное действие привычки
        self.assertEqual(response.data['action'], 'Читать 30 минут')
