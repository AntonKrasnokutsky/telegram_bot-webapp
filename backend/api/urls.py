from django.urls import include, path

from .views import (
    PointsViewSet,
    RepairViewSet,
    RepairViewASet,
    ServicesViewSet,
    ServicesViewASet
)

app_name = 'api'


urlpatterns = [
    path('points/', PointsViewSet.as_view({'get': 'list'})),
    path('services/', ServicesViewSet.as_view({'get': 'list'})),
    path('repairs/', RepairViewSet.as_view({'get': 'list'})),
    path(
        'v2/services/',
        ServicesViewASet.as_view(
            {
                'get': 'list',
                'post': 'create'
            }),
        name='services_v2'),
    path('v2/repairs/', RepairViewASet.as_view({'get': 'list'})),
    path('auth/', include('djoser.urls.authtoken')),

]
