from django.urls import path
from web_page.views.settings.views import index

urlpatterns = [
    path("", index, name="settings_index"),
]
