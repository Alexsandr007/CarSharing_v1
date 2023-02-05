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
    Bearing, Speed, XY
from simple_history.admin import SimpleHistoryAdmin


admin.site.register(Device)
admin.site.register(XY)
admin.site.register(Speed)
admin.site.register(Bearing)
admin.site.register(Data)
admin.site.register(AllActivityMetrics)


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
