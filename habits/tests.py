from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from habits.models import Habit


class HabitTests(APITestCase):

    def setUp(self):
        """Настройка тестового окружения."""
        self.user1_data = {'email': 'user1@example.com', 'password': 'password123'}
        self.user1 = self.client.post(reverse('user-register'), self.user1_data, format='json').data
        self.client.force_authenticate(self.client.post(reverse('user-login'), self.user1_data, format='json').data) # Аутентификация для user1

        self.user2_data = {'email': 'user2@example.com', 'password': 'password456'}
        self.user2 = self.client.post(reverse('user-register'), self.user2_data, format='json').data
        self.client_user2 = self.client.__class__() # Создаем новый клиент для user2
        self.client_user2.force_authenticate(self.client.post(reverse('user-login'), self.user2_data, format='json').data) # Аутентификация для user2


        self.habit1_data = {
            'name': 'Утренняя зарядка',
            'description': 'Растяжка и легкие упражнения',
            'period': 'daily',
            'target_times': 1,
            'is_public': False,
            'color': '#FF5733'
        }
        # Создаем привычку для user1
        response = self.client.post(reverse('habit-list'), self.habit1_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.habit1 = Habit.objects.get(pk=response.data['id'], owner=User.objects.get(email='user1@example.com'))

        self.habit2_data = {
            'name': 'Читать 30 минут',
            'description': 'Чтение художественной литературы',
            'period': 'weekly',
            'target_times': 7, # 7 раз в неделю
            'is_public': True,
            'color': '#33FF57'
        }
        # Создаем публичную привычку для user1
        response = self.client.post(reverse('habit-list'), self.habit2_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.habit2 = Habit.objects.get(pk=response.data['id'], owner=User.objects.get(email='user1@example.com'))

        self.habit3_data = {
            'name': 'Медитация',
            'description': 'Практика осознанности',
            'period': 'daily',
            'target_times': 1,
            'is_public': False,
            'color': '#3357FF'
        }
        # Создаем привычку для user2
        response = self.client_user2.post(reverse('habit-list'), self.habit3_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.habit3 = Habit.objects.get(pk=response.data['id'], owner=User.objects.get(email='user2@example.com'))

        # URL-адреса
        self.list_url = reverse('habit-list')
        self.detail_url = lambda id: reverse('habit-detail', kwargs={'pk': id})
        self.log_create_url = lambda habit_id: reverse('habit-log-create', kwargs={'habit_id': habit_id})
        self.public_list_url = reverse('habit-public-list')


    def test_habit_creation(self):
        """Тестирование создания новой привычки."""
        self.assertEqual(Habit.objects.count(), 3) # 3 привычки созданы в setUp
        self.assertEqual(self.habit1.owner, User.objects.get(email='user1@example.com'))
        self.assertEqual(self.habit1.name, 'Утренняя зарядка')

    def test_habit_list_own(self):
        """Тестирование получения списка своих привычек."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # user1 должен видеть свои 2 привычки
        self.assertEqual(response.data[0]['name'], 'Утренняя зарядка')
        self.assertEqual(response.data[1]['name'], 'Читать 30 минут')

    def test_habit_list_other_user_habits_hidden(self):
        """Тестирование, что пользователь не видит чужие приватные привычки."""
        response = self.client.get(self.list_url)
        user1_habit_ids = {h['id'] for h in response.data}

        response_user2 = self.client_user2.get(self.list_url)
        user2_habit_ids = {h['id'] for h in response_user2.data}

        self.assertNotIn(self.habit3.id, user1_habit_ids) # user1 не должен видеть habit3 (user2)
        self.assertNotIn(self.habit1.id, user2_habit_ids) # user2 не должен видеть habit1 (user1)
        self.assertNotIn(self.habit2.id, user2_habit_ids) # user2 не должен видеть habit2 (user1)


    def test_habit_retrieve_detail(self):
        """Тестирование получения деталей одной привычки."""
        url = self.detail_url(self.habit1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Утренняя зарядка')

    def test_habit_retrieve_detail_forbidden_other_user(self):
        """Тестирование попытки получить детали чужой приватной привычки."""
        url = self.detail_url(self.habit3.id) # Привычка user2
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Или 404, если скрывается

    def test_habit_retrieve_detail_public_other_user(self):
        """Тестирование получения деталей чужой публичной привычки."""
        url = self.detail_url(self.habit2.id) # Публичная привычка user1
        response = self.client_user2.get(url) # Запрашиваем от user2
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Читать 30 минут')

    def test_habit_update(self):
        """Тестирование обновления привычки."""
        url = self.detail_url(self.habit1.id)
        update_data = {'name': 'Вечерняя зарядка', 'color': '#ABCDEF'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Вечерняя зарядка')
        self.assertEqual(response.data['color'], '#ABCDEF')

        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.name, 'Вечерняя зарядка')

    def test_habit_update_forbidden_other_user(self):
        """Тестирование попытки обновить чужую привычку."""
        url = self.detail_url(self.habit3.id) # Привычка user2
        update_data = {'name': 'Попытка взлома'}
        response = self.client.patch(url, update_data, format='json') # user1 пытается обновить
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_destroy(self):
        """Тестирование удаления привычки."""
        url = self.detail_url(self.habit1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(owner=User.objects.get(email='user1@example.com')).count(), 1) # Осталась habit2

    def test_habit_destroy_forbidden_other_user(self):
        """Тестирование попытки удалить чужую привычку."""
        url = self.detail_url(self.habit3.id) # Привычка user2
        response = self.client.delete(url) # user1 пытается удалить
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_habit_list(self):
        """Тестирование получения списка публичных привычек."""
        response = self.client.get(self.public_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Только habit2 (публичная user1)
        self.assertEqual(response.data[0]['name'], 'Читать 30 минут')

    def test_log_create(self):
        """Тестирование создания записи лога для привычки."""
        url = self.log_create_url(self.habit1.id)
        now = timezone.now()
        log_data = {'log_time': now.isoformat(), 'count': 1}
        response = self.client.post(url, log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['habit'], self.habit1.id)
        self.assertEqual(response.data['count'], 1)

        # Проверяем, что last_done у habit1 обновилось
        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.last_done.replace(microsecond=0), now.replace(microsecond=0))

    def test_log_create_multiple_logs(self):
        """Тестирование создания нескольких логов для одной привычки."""
        url = self.log_create_url(self.habit2.id) # habit2 - читать 7 раз в неделю
        log_time_1 = timezone.now()
        response1 = self.client.post(url, {'log_time': log_time_1.isoformat(), 'count': 1}, format='json')

        log_time_2 = timezone.now() + timezone.timedelta(days=1)
        response2 = self.client.post(url, {'log_time': log_time_2.isoformat(), 'count': 1}, format='json')

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Проверяем, что last_done обновилось на последнее
        self.habit2.refresh_from_db()
        self.assertEqual(self.habit2.last_done.replace(microsecond=0), log_time_2.replace(microsecond=0))

        # Проверяем общее количество выполнений (если ведем счетчик)
        # count_logs = Log.objects.filter(habit=self.habit2).count() # Если у Log есть поле habit
        # self.assertEqual(count_logs, 2)

    def test_log_create_invalid_count(self):
        """Тестирование создания лога с невалидным количеством."""
        url = self.log_create_url(self.habit1.id)
        # Предполагаем, что target_times = 1, а count = 2 - это ошибка
        log_data = {'log_time': timezone.now().isoformat(), 'count': 2}
        response = self.client.post(url, log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('count', response.data)

    def test_log_create_forbidden_other_user(self):
        """Тестирование попытки создать лог для чужой привычки."""
        url = self.log_create_url(self.habit3.id) # Привычка user2
        log_data = {'log_time': timezone.now().isoformat(), 'count': 1}
        response = self.client.post(url, log_data, format='json') # user1 пытается логгировать
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)