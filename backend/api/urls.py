from django.urls import path

from .views import PointsViewSet

app_name = 'api'

urlpatterns = [
    path('points/', PointsViewSet.as_view({'post': 'create'})),
]
