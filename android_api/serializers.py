from django.core.exceptions import ValidationError
from rest_framework import serializers

from android_api.models import TimeStampSetting, Device


class TelegramUntieViewSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(required=True)


class RegisterDriverSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(required=True)
    driver_id = serializers.CharField(required=True)


class CheckTelegramAuthSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(required=True)


class TelegramConfirmationViewSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(required=True)
    is_telegram_activated = serializers.BooleanField(read_only=True)


class DeviceSerializer(serializers.ModelSerializer):
    okodrive_status = serializers.CharField(read_only=True)
    is_telegram_activated = serializers.BooleanField(read_only=True)
    driver_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Device
        exclude = ('created_at', 'updated_at')


class TimeStampSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeStampSetting
        exclude = ('created_at', 'updated_at')
