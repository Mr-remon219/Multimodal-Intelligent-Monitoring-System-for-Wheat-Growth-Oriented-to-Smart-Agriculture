from django.urls import path
from web_page.views.log.views import index, register_api, register_page

urlpatterns = [
    path("", index, name="log_index"),
    path("register/", register_page, name="register_page"),
    path("api/register/", register_api, name="register_api"),
]
