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
    ActivityTypes, ConfirmationTelegram
from android_api.serializers import TimeStampSettingSerializer, DeviceSerializer, RegisterDriverSerializer, \
    CheckTelegramAuthSerializer, TelegramConfirmationViewSerializer, TelegramUntieViewSerializer
from android_api.services.get_okodrive_status import get_okodrive_status
from android_api.services.unix_format_converter import unix_converter
from android_api.services.generate_device_id import gen_smth


class RegisterDriverView(APIView):

    @swagger_auto_schema(
        operation_description="A request for registering a driver in the bot and assigning him a driver_id, as well as "
                              "creating an application for telegram confirmation from the application.",
        request_body=RegisterDriverSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterDriverSerializer(data=request.data)
        if serializer.is_valid():
            if not Device.objects.filter(device_id=serializer.validated_data['device_id']).exists():
                return Response({
                    "status": False,
                    "error_text": 'Такого девайса не существует'
                }, status=status.HTTP_200_OK)
            if Device.objects.filter(driver_id=serializer.validated_data['driver_id']).exists():
                return Response({
                    "status": False,
                    "error_text": 'Телеграмм привязан к устройству: {0}'.format(serializer.validated_data['device_id'])
                })


            obj = Device.objects.get(device_id=serializer.validated_data['device_id'])
            # obj.is_telegram_activated = True
            # request_telegram = ConfirmationTelegram.objects.create(device_id=serializer.validated_data['device_id'],is_telegram_activated=False)
            obj.driver_id = serializer.validated_data['driver_id']
            # request_telegram.save()
            obj.save()

            return Response({
                "status": True,
                "message": 'Авторизация пользователя прошла успешно'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckTelegramAuthView(APIView):

    @swagger_auto_schema(
        operation_description="Returns information about whether the specified device is linked to a Telegram account. Used by the 1c server",
        responses={
            204: "Данного устройства не существует",
            200: ''
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            obj = Device.objects.get(device_id=kwargs['device_id'])
            if obj.is_telegram_activated:
                return Response({
                    "status": True,
                    "message": "Телеграмм привязан к устройству"
                }, status=status.HTTP_200_OK)
            return Response({
                "status": False,
                "message": "Телеграмм не привязан к устройству"
            }, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)


class TelegramConfirmationView(APIView):

    @swagger_auto_schema(
        operation_description="The request used to confirm the telegram binding application from the application.",
        request_body=TelegramConfirmationViewSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = TelegramConfirmationViewSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # obj = ConfirmationTelegram.objects.get(device_id=serializer.validated_data['device_id'], is_telegram_activated=False)
                # obj.is_telegram_activated = True
                device = Device.objects.get(device_id=serializer.validated_data['device_id'])
                device.is_telegram_activated = True
                # if obj.is_telegram_activated:
                if device.is_telegram_activated:
                    # obj.save()
                    device.save()
                    return Response({
                        "status": True,
                        "message": 'Телеграмм привязан'
                    }, status=status.HTTP_200_OK)
                # obj.save()
                device.save()
                return Response({
                    "status": False,
                    "message": "Телеграмм не привязан к устройству"
                }, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @method_decorator(name='list', decorator=swagger_auto_schema(
#     operation_description="The request used by the mobile application to get the intervals at which the telemetry "
#                               "is updated, under the 'put' request to the telemetry",
# ))
class TimeStampSettingView(ListAPIView):
    serializer_class = TimeStampSettingSerializer
    queryset = TimeStampSetting.objects.all()
    permission_classes = [AllowAny]

# @method_decorator(name='perform_create', decorator=swagger_auto_schema(
#     operation_description="A request to record the device's primary telemetry and assign a unique device_id to it,"
#                           " as well as to determine its Oko_drive status.",
# ))
class DeviceViewSet(ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [AllowAny]


    def perform_create(self, serializer):
        if serializer.validated_data['is_stopped'] is True:
            okodrive_status = OkoDriveStatuses.ignore
        elif serializer.validated_data['app_type'] == AppTypes.mirror:
            okodrive_status = OkoDriveStatuses.in_car
        else:
            okodrive_status = get_okodrive_status(
                serializer.validated_data['activity_type'],
                serializer.validated_data['speed']
            )
        speed_kph = serializer.validated_data['speed']
        unix_timestamp = int(time.time())
        generate_id = gen_smth(3)
        serializer.save(
            device_id=generate_id,
            location=f"{serializer.validated_data['longitude']}, {serializer.validated_data['latitude']}",
            okodrive_status=okodrive_status,
            speed=speed_kph,
            last_message_timestamp_utc=unix_timestamp,
            last_message_timestamp_txt_utc=unix_converter(unix_timestamp),
            yandex_link=f"https://yandex.ru/maps/?pt="
                        f"{serializer.validated_data['longitude']},{serializer.validated_data['latitude']}&z=18&l=map"
        )

    # @method_decorator(name='perform_update', decorator=swagger_auto_schema(
    #     operation_description="A request to re-record device telemetry changes to the DeviceHistory"
    #                           " table and also to determine its Oko_drive status at the current moment.",
    # ))
    def perform_update(self, serializer):
        if serializer.validated_data['is_stopped'] is True:
            okodrive_status = OkoDriveStatuses.ignore
        elif serializer.validated_data['app_type'] == AppTypes.mirror:
            okodrive_status = OkoDriveStatuses.in_car
        else:
            print(serializer)
            okodrive_status = get_okodrive_status(
                serializer.validated_data['activity_type'],
                serializer.validated_data['speed'],
                device_id=self.get_object().device_id
            )
        speed_kph = serializer.validated_data['speed']
        unix_timestamp = int(time.time())
        if serializer.validated_data['longitude'] and serializer.validated_data['latitude']:
            serializer.save(
                device_id = serializer.validated_data['device_id'],
                last_message_timestamp_txt_utc=unix_converter(unix_timestamp),
                last_message_timestamp_utc=unix_timestamp,
                okodrive_status=okodrive_status,
                speed=speed_kph,
                location=f"{serializer.validated_data['longitude']}, {serializer.validated_data['latitude']}",
                yandex_link=f"https://yandex.ru/maps/?pt="
                            f"{serializer.validated_data['longitude']},{serializer.validated_data['latitude']}&z=18&l=map"),


class TelegramUntieView(APIView):

    @swagger_auto_schema(
        operation_description="Request to unlink account telegrams from the device",
        request_body=TelegramUntieViewSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = TelegramUntieViewSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = Device.objects.get(device_id=serializer.validated_data['device_id'])
                if not obj.is_telegram_activated:
                    return Response({
                        "status": True,
                        "message": "Телеграмм не был привязан"
                    }, status=status.HTTP_200_OK)
                obj.is_telegram_activated = False
                obj.save()
                return Response({
                    "status": False,
                    "message": "Телеграмм отвязан от устройства"
                }, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
