from django.urls import path
from web_page.views.main.views import (
    index,
    latest_sensor_prediction_api,
    sensor_prediction_stream_api,
    predict_batch_api,
    predict_simple_api,
)

urlpatterns = [
    path("", index, name="main_page"),
    path("api/predict/simple/", predict_simple_api, name="predict_simple_api"),
    path("api/predict/batch/", predict_batch_api, name="predict_batch_api"),
    path("api/sensor/latest/", latest_sensor_prediction_api, name="latest_sensor_prediction_api"),
    path("api/sensor/stream/", sensor_prediction_stream_api, name="sensor_prediction_stream_api"),
]
