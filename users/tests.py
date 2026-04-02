from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(APITestCase):

    def setUp(self):
        """Настройка тестового окружения."""
        self.user_data = {'username': 'testuser', 'email': 'test@test.com', 'password': 'password123'}
        self.user = User.objects.create_user(**self.user_data)
        self.register_url = reverse('users:register')
        self.login_url = reverse('token_obtain_pair')
        self.profile_url = reverse('users:user-profile')

    def test_user_registration(self):
        """Тестирование успешной регистрации пользователя."""
        url = self.register_url
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(User.objects.count(), 2) # Первый пользователь из setUp + новый
        new_user = User.objects.get(email='newuser@example.com')
        self.assertTrue(new_user.check_password('newpassword456'))

    def test_user_registration_duplicate_email(self):
        """Тестирование регистрации с уже существующей почтой."""
        url = self.register_url
        data = {
            'username': 'another_user',
            'email': self.user_data['email'],
            'password': 'anotherpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(User.objects.filter(email=self.user_data['email']).count(), 1)

    def test_user_login(self):
        """Тестирование успешного входа пользователя."""
        url = self.login_url
        response = self.client.post(url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Тестирование входа с неверными учетными данными."""
        url = self.login_url
        invalid_data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, invalid_data, format='json')

        # Теперь SimpleJWT должен вернуть 401 (неверные учетные данные), а не 400
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_user_profile_retrieve(self):
        """Тестирование получения профиля пользователя (аутентифицированным)."""
        self.client.force_authenticate(user=self.user) # Аутентификация клиента
        url = self.profile_url
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_profile_retrieve_unauthenticated(self):
        """Тестирование получения профиля анонимным пользователем."""
        url = self.profile_url
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_update(self):
        """Тестирование обновления профиля пользователя."""
        self.client.force_authenticate(user=self.user)
        url = self.profile_url
        new_data = {'email': 'updateduser@example.com', 'first_name': 'UpdatedName'}
        response = self.client.patch(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updateduser@example.com')
        self.assertEqual(response.data['first_name'], 'UpdatedName')

        # Обновляем пользователя в базе данных и проверяем
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updateduser@example.com')
        self.assertEqual(self.user.first_name, 'UpdatedName')

    def test_user_profile_update_other_user(self):
        """Тестирование попытки обновить профиль другого пользователя."""
        other_user = User.objects.create_user(
            username='other_guy',
            email='other@guy.com',
            password='password123'
        )
        other_profile_url = reverse('users:user-profile', kwargs={'pk': other_user.pk})

        self.client.force_authenticate(user=self.user)
        new_data = {'email': 'hacked@example.com'}
        response = self.client.patch(other_profile_url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Или 404, зависит от реализации
        other_user.refresh_from_db()
        self.assertEqual(other_user.email, 'other@example.com') # Email не изменился