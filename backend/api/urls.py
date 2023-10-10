from django.urls import path
# from rest_framework import routers

from .views import PointsViewSet, post_image

app_name = 'api'

# router = routers.DefaultRouter()
# router.register(
#     'points',
#     PointsViewSet
# )

urlpatterns = [
    path('points/', PointsViewSet.as_view({'post': 'create'})),
    path('image/', post_image, name='post_image')
    # path('', include(router.urls)),
]
