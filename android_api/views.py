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
    ActivityTypes, Bearing, Speed, XY, AllActivityMetrics, Data, OkoDriveStatusActive
from android_api.serializers import DeviceSerializer, DataSerializer, AllActivityMetricsSerializer, XYSerializer, SpeedSerializer, \
    BearingSerializer
from android_api.services.get_okodrive_status import get_okodrive_status
from android_api.services.unix_format_converter import unix_converter
from android_api.services.generate_device_id import gen_smth

from django.db.models import Q


class DeviceViewSet(ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        okodrive_status = get_okodrive_status(
                    serializer.validated_data['data']['activity'],
                    serializer.validated_data['data']['speed']['value'],
                    device_id=serializer.validated_data['device_id'],
                    activity=serializer.validated_data['data']['activity'],
                )
        generate_id = gen_smth(3)
        if serializer.validated_data['data']['xy']['longitude'] and serializer.validated_data['data']['xy']['latitude']:
            bearing = Bearing(value=serializer.validated_data['data']['bearing']['value'],
                              accuracy=serializer.validated_data['data']['bearing']['accuracy'])
            bearing.save()
            speed = Speed(value=serializer.validated_data['data']['speed']['value'],
                          accuracy=serializer.validated_data['data']['speed']['accuracy'])
            speed.save()
            xy = XY(latitude=serializer.validated_data['data']['xy']['latitude'],
                    longitude=serializer.validated_data['data']['xy']['longitude'],
                    accuracy=serializer.validated_data['data']['xy']['accuracy'])
            xy.save()
            data = Data()
            data.bearing = bearing
            data.speed = speed
            data.xy = xy
            data.activity = serializer.validated_data['data']['activity']
            data.save()
            for i in serializer.validated_data['data']['all_activity_metrics']:
                all_activity_metrics = AllActivityMetrics(activity=i['activity'], confidence=i['confidence'])
                all_activity_metrics.save()
                data.all_activity_metrics.add(all_activity_metrics)
            data.save()
            print(serializer.validated_data['device_id'])
            print(okodrive_status)
            oko_drive_status_active = OkoDriveStatusActive(device_id=generate_id, activity_status=okodrive_status)
            oko_drive_status_active.save()
            serializer.save(device_id=generate_id, data=data)

    def perform_update(self, serializer):
        print(serializer)
        okodrive_status = get_okodrive_status(
            serializer.validated_data['data']['activity'],
            serializer.validated_data['data']['speed']['value'],
            device_id=serializer.validated_data['device_id'],
        )
        if serializer.validated_data['data']['xy']['longitude'] and serializer.validated_data['data']['xy']['latitude']:
            device = Device.objects.get(device_id=serializer.validated_data['device_id'])
            # bearing
            device.data.bearing.value = serializer.validated_data['data']['bearing']['value']
            device.data.bearing.accuracy = serializer.validated_data['data']['bearing']['accuracy']
            # speed
            device.data.speed.value = serializer.validated_data['data']['speed']['value']
            device.data.speed.accuracy = serializer.validated_data['data']['speed']['accuracy']
            # xy
            device.data.xy.latitude = serializer.validated_data['data']['xy']['latitude']
            device.data.xy.longitude = serializer.validated_data['data']['xy']['longitude']
            device.data.xy.accuracy = serializer.validated_data['data']['xy']['accuracy']
            device.data.activity = serializer.validated_data['data']['activity']
            device.data.all_activity_metrics.clear()
            for i in serializer.validated_data['data']['all_activity_metrics']:
                all_activity_metrics = AllActivityMetrics(activity=i['activity'], confidence=i['confidence'])
                all_activity_metrics.save()
                device.data.all_activity_metrics.add(all_activity_metrics)
            device.save()
            oko_drive_status_active = OkoDriveStatusActive.objects.get(
                device_id=serializer.validated_data['device_id'])
            oko_drive_status_active.activity_status = okodrive_status
            oko_drive_status_active.save()
            serializer.save(device_id=serializer.validated_data['device_id'], data=device.data)
