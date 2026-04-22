import datetime
from django.db import models
from django.utils import timezone

class User(models.Model):
    user_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    signup_time = models.DateTimeField(default=timezone.now())


    def __str__(self):
        return self.user_name

    def was_new_user(self):
        return self.signup_time >= timezone.now() - datetime.timedelta(days=7)
