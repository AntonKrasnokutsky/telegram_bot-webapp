from django.urls import path

from .views import points_api, PointsViewSet

app_name = 'api'

urlpatterns = [
    path('points/', PointsViewSet.as_view({'get': 'list', 'post': 'create'})),
]
