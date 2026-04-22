from django.contrib import admin

# Register your models here.

from .models.users import User

admin.site.register(User)
