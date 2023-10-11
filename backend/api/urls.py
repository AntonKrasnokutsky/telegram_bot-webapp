from django.urls import path

from .views import PointsViewSet, post_image, get_photo

app_name = 'api'


urlpatterns = [
    path('points/', PointsViewSet.as_view({'post': 'create'})),
    path('photo/', post_image, name='post_image'),
    path('photo/<str:name>', get_photo)
]
