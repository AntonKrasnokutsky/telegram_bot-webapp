from django.urls import include, path
from rest_framework import routers

from .views import (
    PointsViewSet,
    RepairViewSet,
    RepairViewASet,
    ServicesViewSet,
    ServicesViewASet,
    ServiceManViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(
    'v2/serviceman',
    ServiceManViewSet
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'points/',
        PointsViewSet.as_view({'get': 'list'}),
        name='points'
    ),
    path(
        'services/',
        ServicesViewSet.as_view({'get': 'list'}),
        name='services'
    ),
    path(
        'repairs/',
        RepairViewSet.as_view({'get': 'list'}),
        name='repairs'
    ),
    path(
        'v2/services/',
        ServicesViewASet.as_view(
            {
                'get': 'list',
                'post': 'create'
            }),
        name='services_v2'
    ),
    path(
        'v2/repairs/',
        RepairViewASet.as_view(
            {
                'get': 'list',
                'post': 'create'
            }),
        name='repairs_v2'
    ),
    path('auth/', include('djoser.urls.authtoken')),

]
