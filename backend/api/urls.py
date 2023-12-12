from django.urls import include, path

from .views import PointsViewSet, RepairViewSet, RepairViewASet, ServicesViewSet

app_name = 'api'


urlpatterns = [
    path('points/', PointsViewSet.as_view({'get': 'list'})),
    path('services/', ServicesViewSet.as_view({'get': 'list'})),
    path('repairs/', RepairViewSet.as_view({'get': 'list'})),
    path('repairsa/', RepairViewASet.as_view({'get': 'list'})),
    path('auth/', include('djoser.urls.authtoken')),

]
