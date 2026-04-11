from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')

class UserRegistrationSerializer(serializers.ModelSerializer): # Или как называется ваш сериализатор для регистрации
    password = serializers.CharField(write_only=True, required=True, min_length=8) # Пример

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'email': {
                'required': True,
                'validators': [UniqueValidator(queryset=User.objects.all(), message='Пользователь с таким email уже существует.')]
            },
            'username': {
                'required': True,
                'validators': [UniqueValidator(queryset=User.objects.all(), message='Пользователь с таким именем уже существует.')]
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
