import numbers

from rest_framework import serializers

from points.models import Points

from .models import Events, EventsOfDay, EventsOfPoints

class EventsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Events
        fields = ['event',]


class EventsOfDaySerializer(serializers.ModelSerializer):
    event = serializers.StringRelatedField(source='event.event', read_only=True)

    class Meta:
        model = EventsOfDay
        fields = ['event', 'count', 'date',]


class EventsOfPointsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'view' in self.context:
            if self.context['view'].action not in ('list', 'get'):
                self.fields.update(
                    {
                        'events': serializers.ListField(),
                        'point': serializers.CharField(),
                    })
            else:
                self.fields.update({
                        'events': EventsOfDaySerializer(many=True, ),
                        'point': serializers.StringRelatedField(source='point.name', read_only=True)
                    })
                

    class Meta:
        model = EventsOfPoints
        fields = ['point', ]

    def validate_events(self, value, *args, **kwargs):
        events_init = self.initial_data.get('events')
        events = []
        for event in events_init:
            if not isinstance(event, dict):
                raise serializers.ValidationError(
                    'Поле должно содержать словарь.'
                )
            if not isinstance(event['event'], str):
                raise serializers.ValidationError(
                    'Поле "event" должно содержать название.'
                )
            else:
                get_event, p = Events.objects.get_or_create(event=event['event'])
                print(p)
                print(type(get_event))
                event['event'] = get_event
            if not isinstance(event['count'], numbers.Number):
                raise serializers.ValidationError(
                    'Поле "count" должно быть числом.'
                )
            if not isinstance(event['date'], str):
                raise serializers.ValidationError(
                    'Неправльный формат поля "date".'
                )
            events.append(event)
        return value

    def validate_point(self, value, *args, **kwargs):
        point_init = self.initial_data.get('point')
        if (
            not isinstance(point_init, str)
            or point_init.isdigit()
        ):
            raise serializers.ValidationError(
                    'Поле должо содержать название.'
                )
        try:
            point_valid = Points.objects.get(name=point_init)
        except Points.DoesNotExist:
            raise serializers.ValidationError(
                    f'Название указано неверно. {point_init}'
                )
        return point_valid

    def validate(self, attrs):
        if not attrs['events']:
            raise serializers.ValidationError(
                'Должен быть хотя бы 1 событие.'
            )
        self.fields.update({"events": EventsOfDaySerializer(many=True)})
        return super().validate(attrs)
    
    def create(self, validated_data):
        events = self.validated_data.pop('events')
        # print(self.validated_data)
        # print(events)

        event_of_point = EventsOfPoints.objects.create(**self.validated_data)
        for event in events:
        #     print(type(event['event']))
            event_of_point_day = EventsOfDay.objects.create(**event)
            event_of_point.events.add(event_of_point_day)
        #     EventsPointsOfDay.objects.create(
        #         event_point=event_of_point,
        #         event=EventsOfDay.objects.create(**event),
        #     )
        # event_of_point.events.add(**events)
        return event_of_point
        # print('создание')
        # print(validated_data)
        # return super().create(validated_data)
