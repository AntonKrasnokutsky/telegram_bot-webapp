from django.urls import path

from .views import PointsViewSet, RepairViewSet, ServicesViewSet

app_name = 'api'


urlpatterns = [
    path('points/', PointsViewSet.as_view({'get': 'list'})),
    path('services/', ServicesViewSet.as_view({'get': 'list'})),
    path('repairs/', RepairViewSet.as_view({'get': 'list'})),

]
