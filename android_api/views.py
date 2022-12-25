import time

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


class RegisterDriverView(APIView):

    @swagger_auto_schema(
        operation_description="Registers Device_id by the specified driver_id",
        request_body=RegisterDriverSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterDriverSerializer(data=request.data)
        if serializer.is_valid():
            # если device_id не найден то выполнится
            if not Device.objects.filter(device_id=serializer.validated_data['device_id']).exists():
                return Response({
                    "status": False,
                    "error_text": 'Такого девайса не существует'
                }, status=status.HTTP_200_OK)
            # если driver_id найден то выполнится
            if Device.objects.filter(driver_id=serializer.validated_data['driver_id']).exists():
                return Response({
                    "status": False,
                    "error_text": "Данный driver_id уже зарегестрирован"
                })

            obj = Device.objects.get(device_id=serializer.validated_data['device_id'])
            # obj.is_telegram_activated = True
            request_telegram = ConfirmationTelegram.objects.create(device_id=serializer.validated_data['device_id'],is_telegram_activated=True)
            obj.driver_id = serializer.validated_data['driver_id']
            request_telegram.save()
            obj.save()

            return Response({
                "status": True,
                "message": 'Авторизация пользователя прошла успешно'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckTelegramAuthView(APIView):

    @swagger_auto_schema(
        operation_description="Returns information about whether the specified device is tethered to a telegram account",
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
            return Response({
                "status": False,
                "error_text": "Данного устройства не существует"
            }, status=status.HTTP_204_NO_CONTENT)


class TelegramConfirmationView(APIView):

    @swagger_auto_schema(
        operation_description="Returns information about whether the specified device is tethered to a telegram account",
        request_body=TelegramConfirmationViewSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = TelegramConfirmationViewSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = ConfirmationTelegram.objects.get(device_id=serializer.validated_data['device_id'])
                obj.is_telegram_activated = True
                device = Device.objects.get(device_id=serializer.validated_data['device_id'])
                device.is_telegram_activated = True
                obj.save()
                device.save()
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
                return Response({
                    "status": False,
                    "error_text": "Данного устройства не существует"
                }, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeStampSettingView(ListAPIView):
    serializer_class = TimeStampSettingSerializer
    queryset = TimeStampSetting.objects.all()
    permission_classes = [AllowAny]


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
        speed_kph = serializer.validated_data['speed'] * 3.6
        unix_timestamp = int(time.time())
        serializer.save(
            location=f"{serializer.validated_data['longitude']}, {serializer.validated_data['latitude']}",
            okodrive_status=okodrive_status,
            speed=speed_kph,
            last_message_timestamp_utc=unix_timestamp,
            last_message_timestamp_txt_utc=unix_converter(unix_timestamp),
            yandex_link=f"https://yandex.ru/maps/?pt="
                        f"{serializer.validated_data['longitude']},{serializer.validated_data['latitude']}&z=18&l=map"
        )

    def perform_update(self, serializer):
        if serializer.validated_data['is_stopped'] is True:
            okodrive_status = OkoDriveStatuses.ignore
        elif serializer.validated_data['app_type'] == AppTypes.mirror:
            okodrive_status = OkoDriveStatuses.in_car
        else:
            okodrive_status = get_okodrive_status(
                serializer.validated_data['activity_type'],
                serializer.validated_data['speed'],
                device_id=self.get_object().device_id
            )
        speed_kph = serializer.validated_data['speed'] * 3.6
        unix_timestamp = int(time.time())
        if serializer.validated_data['longitude'] and serializer.validated_data['latitude']:
            serializer.save(
                last_message_timestamp_txt_utc=unix_converter(unix_timestamp),
                last_message_timestamp_utc=unix_timestamp,
                okodrive_status=okodrive_status,
                speed=speed_kph,
                location=f"{serializer.validated_data['longitude']}, {serializer.validated_data['latitude']}",
                yandex_link=f"https://yandex.ru/maps/?pt="
                            f"{serializer.validated_data['longitude']},{serializer.validated_data['latitude']}&z=18&l=map"),



class TelegramUntieView(APIView):

    @swagger_auto_schema(
        operation_description="Returns information about whether the specified device is tethered to a telegram account",
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
                return Response({
                    "status": False,
                    "error_text": "Данного устройства не существует"
                }, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



