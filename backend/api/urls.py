from django.urls import include, path
from rest_framework import routers

from .views import (
    AuditViewSet,
    ExternalRepairViewASet,
    PointsViewSet,
    RepairViewASet,
    ServicesViewASet,
    ServiceManViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(
    'v2/serviceman',
    ServiceManViewSet
)
router.register(
    'v2/externalrepairs',
    ExternalRepairViewASet,
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'points/',
        PointsViewSet.as_view({'get': 'list'}),
        name='points'
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
    path(
        'v2/audit/',
        AuditViewSet.as_view(
            {
                'post': 'create'
            }),
        name='audit_v2'
    ),
    # path(
    #     'v2/externalrepairs/',
    #     ExternalRepairViewASet.as_view(
    #         {
    #             'get': 'list',
    #             'post': 'create'
    #         }),
    #     name='external_repairs_v2'
    # ),
    path('auth/', include('djoser.urls.authtoken')),

]
