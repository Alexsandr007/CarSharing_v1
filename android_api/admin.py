import datetime

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import DateFieldListFilter
from django.utils.safestring import mark_safe

from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter, NumericRangeFilter

from android_api.models import Device, TimeStampSetting, BaseOkoDriveSettings, InVehicleOkoDriveSettings, \
    UnknownOkoDriveSettings, StillOkoDriveSettings, SpeedIntervalSettings, CurrentUTCTime, OnBicycleOkoDriveSettings, \
    OnFootOkoDriveSettings, WalkingOkoDriveSettings, RunningOkoDriveSettings, TiltingOkoDriveSettings, Data, AllActivityMetrics, \
    Bearing, Speed, XY, OkoDriveStatusActive, DeviceHistory
from simple_history.admin import SimpleHistoryAdmin


class WebsiteHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = [
        'last_edited_custom_utc',
        'yandex_link',
        'longitude',
        'latitude',
        'activity_type',
        'okodrive_status',
        'speed',
        'all_activity_metrics',
    ]
    list_display = ['device_id', '__str__', 'last_edited_custom_utc', 'yandex_link_base', 'activity_type', 'okodrive_status', 'speed',
                    'longitude', 'latitude', 'all_activity_metrics']

    list_filter = ('time', 'device_id', 'speed', 'activity_type', 'okodrive_status',)
    search_fields = ['time', 'device_id']
    list_per_page = 500

    def yandex_link(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.yandex_link)
    yandex_link.allow_tags = True

    def yandex_link_base(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.yandex_link)
    yandex_link_base.allow_tags = True

    def last_edited_custom_utc(self, obj):
        return obj.last_edited_custom_utc()


admin.site.register(DeviceHistory, WebsiteHistoryAdmin)

admin.site.register(Device)
admin.site.register(XY)
admin.site.register(Speed)
admin.site.register(Bearing)
admin.site.register(Data)
admin.site.register(AllActivityMetrics)
admin.site.register(OkoDriveStatusActive)



@admin.register(TimeStampSetting)
class TimeStampSettingAdmin(admin.ModelAdmin):
    ...


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
