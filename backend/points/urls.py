from django.urls import path

from .views import Service

app_name = 'points'

urlpatterns = [
    path('service/', Service.as_view()),
]
