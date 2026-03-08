from django.urls import path, include
from web_page.views.index import index

urlpatterns = [
        path("", index, name="index"),
        path("menu/", include("web_page.urls.menu.index")),
        path("settings/", include("web_page.urls.settings.index")),
        ]
