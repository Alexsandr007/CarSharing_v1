import time

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from android_api.models import TimeStampSetting, Device, AppTypes, OkoDriveStatuses, \
    ActivityTypes
from android_api.serializers import DeviceSerializer, DataSerializer, AllActivityMetricsSerializer, XYSerializer, SpeedSerializer, \
    BearingSerializer
from android_api.services.get_okodrive_status import get_okodrive_status
from android_api.services.unix_format_converter import unix_converter
from android_api.services.generate_device_id import gen_smth


class DeviceViewSet(ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        okodrive_status = get_okodrive_status(
                    serializer.validated_data['data']['activity'],
                    serializer.validated_data['data']['speed']['value'],
                    device_id=self.get_object().device_id,
                    activity=serializer.validated_data['data']['activity'],
                    speed=serializer.validated_data['data']['speed']['value']
                )
        unix_timestamp = int(time.time())
        generate_id = gen_smth(3)
        json_array = []
        for i in serializer.validated_data['data']['all_activity_metrics']:
            json_array.append({'activity': i['activity'], 'confidence': i['confidence']})
        if serializer.validated_data['data']['xy']['longitude'] and serializer.validated_data['data']['xy']['latitude']:
            serializer.save(
                data={
                    'device_id': generate_id,
                    'data': {
                        'bearing': {
                            'value': serializer.validated_data['data']['bearing']['value'],
                            'accuracy': serializer.validated_data['data']['bearing']['accuracy']
                        },
                        'speed': {
                            'value': serializer.validated_data['data']['speed']['value'],
                            'accuracy': serializer.validated_data['data']['speed']['accuracy']
                        },
                        'xy': {
                            'latitude': serializer.validated_data['data']['xy']['latitude'],
                            'longitude': serializer.validated_data['data']['xy']['longitude'],
                            'accuracy': serializer.validated_data['data']['xy']['accuracy']
                        },
                        'time': unix_timestamp,
                        'activity': okodrive_status,
                        'all_activity_metrics': json_array
                    }
                }
            )

    def perform_update(self, serializer):
        okodrive_status = get_okodrive_status(
            serializer.validated_data['data']['activity'],
            serializer.validated_data['data']['speed']['value'],
            device_id=self.get_object().device_id,
            activity=serializer.validated_data['data']['activity'],
            speed=serializer.validated_data['data']['speed']['value']
        )
        unix_timestamp = int(time.time())
        json_array = []
        for i in serializer.validated_data['data']['all_activity_metrics']:
            json_array.append({'activity': i['activity'], 'confidence': i['confidence']})
        if serializer.validated_data['data']['xy']['longitude'] and serializer.validated_data['data']['xy']['latitude']:
            serializer.save(
                data={
                    'device_id': serializer.validated_data['device_id'],
                    'data': {
                        'bearing': {
                            'value': serializer.validated_data['data']['bearing']['value'],
                            'accuracy': serializer.validated_data['data']['bearing']['accuracy']
                        },
                        'speed': {
                            'value': serializer.validated_data['data']['speed']['value'],
                            'accuracy': serializer.validated_data['data']['speed']['accuracy']
                        },
                        'xy': {
                            'latitude': serializer.validated_data['data']['xy']['latitude'],
                            'longitude': serializer.validated_data['data']['xy']['longitude'],
                            'accuracy': serializer.validated_data['data']['xy']['accuracy']
                        },
                        'time': unix_timestamp,
                        'activity': okodrive_status,
                        'all_activity_metrics': json_array
                    }
                }
            )
