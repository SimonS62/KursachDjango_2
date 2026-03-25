from django.db import models
from django.conf import settings


class TelegramUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_profile')
    chat_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
def __str__(self):
    return f"{self.user.username} - {self.chat_id}"
