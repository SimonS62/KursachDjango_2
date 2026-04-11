from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserRegistrationSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение для всех, но запись только для владельца.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user

class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Получение и обновление профиля пользователя"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return User.objects.get(pk=user_id)
