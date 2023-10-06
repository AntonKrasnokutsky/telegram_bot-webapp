from django.urls import path

from .views import points_api

app_name = 'api'

urlpatterns = [
    path('points/', points_api),
]
