from django.urls import path

from .views import (
    AuditView,
    AuditListFilteredView,
    FuelCompensationListView,
    FuelCompensationCreateView,
    ServicesListView,
    ServicesView,
    RepairsView,
    TypeWorkRepairsListView,
    TypeWorkRepairsCreateView,
    RepairsListFilteredView,
    ServiceListFilteredView,
)

app_name = 'points'

urlpatterns = [
    path(
        'service/',
        ServicesView.as_view()
    ),
    path(
        'repair/',
        RepairsView.as_view()
    ),
    path(
        'services_list/',
        ServicesListView.as_view(),
        name='services_list'
    ),
    path(
        'repairs_list/',
        RepairsListFilteredView.as_view(),
        name='repairs_list'
    ),
    path(
        'typeworkrepairs/',
        TypeWorkRepairsListView.as_view(),
        name='typeworkrepairs'
    ),
    path(
        'typeworkrepairs/add/',
        TypeWorkRepairsCreateView.as_view(),
        name='typeworkrepairs_add'
    ),
    path(
        'service_list/',
        ServiceListFilteredView.as_view(),
        name='service_list'
    ),
    path(
        'fuel_list/',
        FuelCompensationListView.as_view(),
        name='fuelcompensations'
    ),
    path(
        'fuel_create/',
        FuelCompensationCreateView.as_view(),
        name='fuelcompensations_add'
    ),
    path(
        'audit/',
        AuditView.as_view()
    ),
    path(
        'audit_list/',
        AuditListFilteredView.as_view(),
        name='audit_list'
    ),
]
