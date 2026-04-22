from django.urls import path
from web_page.views.main.views import index

urlpatterns = [
    path("", index, name="main_page"),
]
