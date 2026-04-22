import datetime
import secrets
import string
from django.db import models
from django.utils import timezone


def generate_sensor_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class User(models.Model):
    user_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    signup_time = models.DateTimeField(default=timezone.now)
    sensor_key = models.CharField(max_length=32, unique=True, default=generate_sensor_key)


    def __str__(self):
        return self.user_name

    def was_new_user(self):
        return self.signup_time >= timezone.now() - datetime.timedelta(days=7)
