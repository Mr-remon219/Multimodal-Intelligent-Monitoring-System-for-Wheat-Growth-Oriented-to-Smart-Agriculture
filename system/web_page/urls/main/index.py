from django.urls import path
from web_page.views.main.views import index, predict_batch_api, predict_simple_api

urlpatterns = [
    path("", index, name="main_page"),
    path("api/predict/simple/", predict_simple_api, name="predict_simple_api"),
    path("api/predict/batch/", predict_batch_api, name="predict_batch_api"),
]
