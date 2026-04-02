from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.views import UserRegistrationView, UserProfileView
from telegram_bot.views import TelegramWebhookView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/habits/', include('habits.urls')),

    # DRF browsable API
    path('api/auth/', include('rest_framework.urls')),


    # Документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Телеграм
    path('telegram/webhook/', TelegramWebhookView.as_view(), name='telegram-webhook'),

    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]

