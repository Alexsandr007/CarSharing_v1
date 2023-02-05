from django.core.exceptions import ValidationError
from rest_framework import serializers

from android_api.models import TimeStampSetting, Device, Bearing, Speed, XY, AllActivityMetrics


class BearingSerializer(serializers.Serializer):
    value = serializers.FloatField()
    accuracy = serializers.FloatField()


class SpeedSerializer(serializers.Serializer):
    value = serializers.FloatField()
    accuracy = serializers.FloatField()


class XYSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    accuracy = serializers.FloatField()


class AllActivityMetricsSerializer(serializers.Serializer):
    activity = serializers.CharField(max_length=25)
    confidence = serializers.IntegerField()


class DataSerializer(serializers.Serializer):
    bearing = BearingSerializer()
    speed = SpeedSerializer()
    xy = XYSerializer()
    time = serializers.DateTimeField()
    activity = serializers.CharField(max_length=25)
    all_activity_metrics = AllActivityMetricsSerializer(many=True)


class DeviceSerializer(serializers.ModelSerializer):
    device_id = serializers.IntegerField()
    data = DataSerializer()

    class Meta:
        model = Device
        fields = '__all__'
        depth = 2


class TimeStampSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeStampSetting
        exclude = ('created_at', 'updated_at')
