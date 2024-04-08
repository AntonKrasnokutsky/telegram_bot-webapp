from django.urls import path

from .views import (
    FuelCompensationListView,
    FuelCompensationCreateView,
    RepairsListView,
    ServicesListView,
    ServicesView,
    RepairsView,
    TypeWorkRepairsListView,
    TypeWorkRepairsCreateView,
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
        RepairsListView.as_view(),
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
        name='typeworkrepairsadd'
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
        name='fuelcompensations_create'
    ),
]
