from django.urls import path
from web_page.views.log.views import index

urlpatterns = [
    path("", index, name="log_index"),
]
