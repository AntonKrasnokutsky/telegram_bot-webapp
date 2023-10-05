
import base64

from http import HTTPStatus

from django.core.files.base import ContentFile
from rest_framework import serializers

from points.models import Points


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, image_string = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_string),
                name=f'temp.{ext}'
            )
        return super().to_internal_value(data)


class PointsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            'view' in self.context
            and self.context['view'].action == 'create'
        ):
            Points.objects.all().delete()

    class Meta:
        model = Points
        fields = ['names', ]

    def validate(self, attrs):
        if not attrs['names']:
            raise serializers.ValidationError(
                'Должно быть хотя бы 1 имя'
            )
        return True

    def create(self, *args, **kwargs):
        names = self.validated_data.pop('names')
        for name in names:
            Points.objects.create(name=name)

        return HTTPStatus.CREATED
