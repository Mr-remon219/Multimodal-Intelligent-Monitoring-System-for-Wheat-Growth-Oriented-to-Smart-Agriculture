from django.urls import path

from web_page.views.sensor.views import upload_by_sensor_key

urlpatterns = [
    path("<str:sensor_key>/upload/", upload_by_sensor_key, name="sensor_upload_by_key"),
]
