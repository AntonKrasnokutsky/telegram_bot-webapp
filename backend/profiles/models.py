from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    office_engineer = models.BooleanField(default=False, blank=True, null=True)
