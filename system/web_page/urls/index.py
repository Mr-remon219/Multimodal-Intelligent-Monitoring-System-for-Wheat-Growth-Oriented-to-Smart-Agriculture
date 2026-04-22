from django.urls import path, include
from web_page.views.index import index, TestView

urlpatterns = [
        path("", index, name="index"),
        path("log/", include("web_page.urls.log.index")),
        path("settings/", include("web_page.urls.settings.index")),
        path("main/", include("web_page.urls.main.index")),
        path("sensor/", include("web_page.urls.sensor.index")),
        ]
