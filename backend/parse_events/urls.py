from django.urls import include, path
from rest_framework import routers

from .views import (
    EventsViewSet,
    # EventsOfDayViewSet,
    EventsOfPointsViewSet,
)

app_name = 'parse_events'

router = routers.DefaultRouter()
router.include_root_view = False
router.register(
    'events',
    EventsViewSet,
    basename='events',
)
router.register(
    'events_of_points',
    EventsOfPointsViewSet,
    basename='events_of_points',
)

urlpatterns = [
    path('v2/parse_events/', include(router.urls)),
]
