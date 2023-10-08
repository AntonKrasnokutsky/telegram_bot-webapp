from django.urls import path

from .views import SomeTemplateView

app_name = 'points'

urlpatterns = [
    path('service/', SomeTemplateView.as_view()),
]
