import datetime

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import DateFieldListFilter
from django.utils.safestring import mark_safe

from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter

from android_api.models import Device, TimeStampSetting, DeviceHistory, BaseOkoDriveSettings, InVehicleOkoDriveSettings, \
    UnknownOkoDriveSettings, StillOkoDriveSettings, SpeedIntervalSettings, CurrentUTCTime, OnBicycleOkoDriveSettings, \
    OnFootOkoDriveSettings, WalkingOkoDriveSettings, RunningOkoDriveSettings, TiltingOkoDriveSettings, ConfirmationTelegram
from simple_history.admin import SimpleHistoryAdmin


class WebsiteHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = [
        'yandex_location_url',
        'longitude',
        'latitude',
        'activity_type',
        'speed',
    ]
    list_filter = ('created_at', 'updated_at')
    list_display = ['device_id', '__str__', 'updated_at']
    search_fields = ['created_at', 'updated_at']
    list_per_page = 500

    def yandex_location_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.yandex_link)
    yandex_location_url.allow_tags = True


admin.site.register(Device, WebsiteHistoryAdmin)




@admin.register(DeviceHistory)
class DeviceHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'device_id',
        'driver_id',
        'is_telegram_activated',
        'last_edited_custom_utc',
        'yandex_location',
        'longitude',
        'latitude',
        'is_stopped',
        'app_type',
        'activity_type',
        'okodrive_status',
        'device_speed',
        'error_name',
        'satellites',
        'accuracy',
        'bearing',
        'device_altitude',
        'acceleration_x',
        'acceleration_y',
        'acceleration_z',
        'charging',
        'battery_percent',
        'network_type',
    ]
    list_filter = (
        ('created_at', DateTimeRangeFilter),
        'app_type',
        'is_telegram_activated',
        'activity_type',
        'okodrive_status',
        'error_name',
        ('longitude', NumericRangeFilter),
        ('latitude', NumericRangeFilter),
        ('speed', NumericRangeFilter),
        ('satellites', NumericRangeFilter),
        ('accuracy', NumericRangeFilter),
        ('bearing', NumericRangeFilter),
        ('altitude', NumericRangeFilter),
        ('last_message_timestamp_txt_utc', NumericRangeFilter),
        ('battery_percent', NumericRangeFilter),
        ('acceleration_x', NumericRangeFilter),
        ('acceleration_y', NumericRangeFilter),
        ('acceleration_z', NumericRangeFilter)
    )
    search_fields = ['device_id', 'activity_type', 'network_type', 'charging']
    list_per_page = 500

    def yandex_location(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.yandex_link)
    yandex_location.allow_tags = True

    def device_speed(self, obj):
        return round(obj.speed, 1)

    def device_altitude(self, obj):
        return round(obj.altitude, 1)

    def last_message(self, obj):
        return obj.last_message_timestamp_txt_utc

    def last_edited_time_txt_utc(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def last_edited_custom_utc(self, obj):
        return obj.last_edited_custom_utc()


@admin.register(TimeStampSetting)
class TimeStampSettingAdmin(admin.ModelAdmin):
    ...

@admin.register(ConfirmationTelegram)
class ConfirmationTelegramAdmin(admin.ModelAdmin):
    list_display = [
        'device_id',
        'is_telegram_activated',
    ]

@admin.register(BaseOkoDriveSettings)
class BaseOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(InVehicleOkoDriveSettings)
class InVehicleOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(UnknownOkoDriveSettings)
class UnknownOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(StillOkoDriveSettings)
class StillOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(OnBicycleOkoDriveSettings)
class StillOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(OnFootOkoDriveSettings)
class StillOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(WalkingOkoDriveSettings)
class StillOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(RunningOkoDriveSettings)
class StillOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(TiltingOkoDriveSettings)
class StillOkoDriveSettingsAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'speed_of_first_interval',
        'speed_of_second_interval',
        'speed_of_third_interval',
        'speed_of_fourth_interval'
    ]


@admin.register(SpeedIntervalSettings)
class SpeedIntervalSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'first_interval', 'second_interval', 'third_interval', 'fourth_interval', 'is_main']


@admin.register(CurrentUTCTime)
class CurrentUTCTimeAdmin(admin.ModelAdmin):
    ...
