from django.urls import path

from .views import ServicesTemplateView, SomeTemplateView

app_name = 'points'

urlpatterns = [
    path(
        'service/',
        SomeTemplateView.as_view(template_name='points/service.html')
    ),
    path(
        'repair/',
        SomeTemplateView.as_view(template_name='points/repair.html')
    ),
    path(
        'services_list/',
        ServicesTemplateView.as_view(),
        name='services_list'
    )

]
