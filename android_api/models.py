from django.db import models
from django.db.models import UniqueConstraint, Q
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from android_api.services.generating_interval_values_dict import get_interval_values_dict


class OkoDriveStatuses(models.TextChoices):
    in_car = 'in_car'
    out_car = 'out_car'
    ignore = 'ignore'
    error = 'error'


class ErrorNames(models.TextChoices):
    in_car = 'in_car'
    out_car = 'out_car'
    none = 'none'


class AppTypes(models.TextChoices):
    phone = 'phone'
    mirror = 'mirror'


class ActivityTypes(models.TextChoices):
    IN_VEHICLE = 'IN_VEHICLE'
    ON_BICYCLE = 'ON_BICYCLE'
    ON_FOOT = 'ON_FOOT'
    WALKING = 'WALKING'
    RUNNING = 'RUNNING'
    STILL = 'STILL'
    TILTING = 'TILTING'
    UNKNOWN = 'UNKNOWN'
    NONE = 'None'


class Device(models.Model):
    device_id = models.IntegerField()
    driver_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    is_telegram_activated = models.BooleanField(default=False)
    longitude = models.FloatField()
    latitude = models.FloatField()
    location = models.CharField(max_length=625, blank=True)
    is_stopped = models.BooleanField()
    app_type = models.CharField(max_length=25, choices=AppTypes.choices)
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    okodrive_status = models.CharField(
        max_length=25,
        blank=True,
        choices=OkoDriveStatuses.choices,
        default=OkoDriveStatuses.ignore)
    state_number = models.CharField(max_length=125, null=True, blank=True)
    speed = models.FloatField()
    satellites = models.PositiveIntegerField(null=True, blank=True)
    accuracy = models.FloatField()
    bearing = models.FloatField()
    client_timestamp = models.PositiveIntegerField()
    altitude = models.FloatField()
    last_message_timestamp_utc = models.PositiveBigIntegerField(null=True, blank=True)
    last_message_timestamp_txt_utc = models.CharField(max_length=625, blank=True, verbose_name='Last message')
    charging = models.BooleanField()
    battery_percent = models.PositiveIntegerField()
    network_type = models.CharField(max_length=12, null=True, blank=True)
    yandex_link = models.CharField(max_length=625, blank=True)
    acceleration_x = models.FloatField()
    acceleration_y = models.FloatField()
    acceleration_z = models.FloatField()
    error_name = models.CharField(max_length=12, blank=True, null=True, choices=ErrorNames.choices)
    history = HistoricalRecords()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Телеметрия устройства'
        verbose_name_plural = 'Телеметрия устройств'
        ordering = ['-created_at']

    def __str__(self):
        return f'Устройство {self.device_id}'


class DeviceHistory(models.Model):
    device_id = models.IntegerField(verbose_name='Device id')
    driver_id = models.CharField(max_length=40, null=True, blank=True)
    is_telegram_activated = models.BooleanField(default=False)
    longitude = models.FloatField(verbose_name='Longitude')
    latitude = models.FloatField(verbose_name='Latitude')
    location = models.CharField(max_length=625, blank=True, verbose_name='Location')
    is_stopped = models.BooleanField()
    app_type = models.CharField(max_length=25, choices=AppTypes.choices)
    activity_type = models.CharField(max_length=25, verbose_name='Activity Type')
    okodrive_status = models.CharField(
        max_length=25,
        blank=True,
        choices=OkoDriveStatuses.choices,
        default=OkoDriveStatuses.ignore)
    speed = models.FloatField(verbose_name='Speed')
    satellites = models.PositiveIntegerField(verbose_name='Satellites', blank=True, null=True)
    accuracy = models.FloatField(verbose_name='Accuracy')
    client_timestamp = models.PositiveIntegerField()
    bearing = models.FloatField(verbose_name='Bearing')
    altitude = models.FloatField(verbose_name='Altitude')
    last_message_timestamp_utc = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name='Last message timestamp utc')
    last_message_timestamp_txt_utc = models.CharField(max_length=625, blank=True)
    charging = models.BooleanField(verbose_name='Charging')
    battery_percent = models.PositiveIntegerField(verbose_name='Battery percent')
    network_type = models.CharField(max_length=12, null=True, blank=True, verbose_name='Network Type')
    yandex_link = models.CharField(max_length=625, blank=True, verbose_name='Yandex link')
    acceleration_x = models.FloatField(verbose_name='Acceleration X')
    acceleration_y = models.FloatField('Acceleration Y')
    acceleration_z = models.FloatField('Acceleration Z')
    error_name = models.CharField(max_length=12, blank=True, null=True, choices=ErrorNames.choices)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Изменено')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'История устройства'
        verbose_name_plural = 'История устройств'
        ordering = ['-device_id', '-created_at']

    def __str__(self):
        return f'Устройство {self.device_id}. Изменено {self.created_at}'

    def last_edited_custom_utc(self):
        utc_settings = CurrentUTCTime.objects.filter(is_main=True).first()
        utc_sign = utc_settings.current_utc[0]
        utc_num = int(utc_settings.current_utc[1])
        last_edited_time = self.created_at
        return (last_edited_time - datetime.timedelta(hours=utc_num)).strftime('%Y-%m-%d %H:%M:%S') if utc_sign == '-' \
            else (last_edited_time + datetime.timedelta(hours=utc_num)).strftime('%Y-%m-%d %H:%M:%S')


class ConfirmationTelegram(models.Model):
    device_id = models.IntegerField(verbose_name='Device id')
    is_telegram_activated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Подтверждение регистрации в телеграме'
        verbose_name_plural = 'Подтверждение регистраций в телеграме'


@receiver(post_save, sender=Device)
def log_device_saved(sender, instance, **kwargs):
    DeviceHistory.objects.create(
        device_id=instance.device_id,
        longitude=instance.longitude,
        driver_id=instance.driver_id,
        is_telegram_activated=instance.is_telegram_activated,
        latitude=instance.latitude,
        location=instance.latitude,
        is_stopped=instance.is_stopped,
        app_type=instance.app_type,
        activity_type=instance.activity_type,
        okodrive_status=instance.okodrive_status,
        speed=instance.speed,
        satellites=instance.satellites,
        accuracy=instance.accuracy,
        client_timestamp=instance.client_timestamp,
        bearing=instance.bearing,
        altitude=instance.altitude,
        last_message_timestamp_utc=instance.last_message_timestamp_utc,
        last_message_timestamp_txt_utc=instance.last_message_timestamp_txt_utc,
        charging=instance.charging,
        battery_percent=instance.battery_percent,
        network_type=instance.network_type,
        yandex_link=instance.yandex_link,
        acceleration_x=instance.acceleration_x,
        acceleration_y=instance.acceleration_y,
        acceleration_z=instance.acceleration_z,
        error_name=instance.error_name
    )


class TimeStampSetting(models.Model):
    min_interval = models.PositiveIntegerField(default=10)
    max_interval = models.PositiveIntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Временная метка'
        verbose_name_plural = 'Временные метки'
        ordering = ['-created_at']


class BaseOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (Базовые типы)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (Базовые типы)'
        ordering =['-activity_type']


class InVehicleOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (IN_VEHICLE)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (IN_VEHICLE)'
        ordering =['-activity_type']


class OnBicycleOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (ON_BICYCLE)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (ON_BICYCLE)'
        ordering =['-activity_type']


class OnFootOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (ON_FOOT)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (ON_FOOT)'
        ordering =['-activity_type']


class WalkingOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (WALKING)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (WALKING)'
        ordering =['-activity_type']


class RunningOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (RUNNING)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (RUNNING)'
        ordering =['-activity_type']


class TiltingOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (TILTING)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (TILTING)'
        ordering =['-activity_type']


class UnknownOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (UNKNOWN)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (UNKNOWN)'
        ordering =['-activity_type']


class StillOkoDriveSettings(models.Model):
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    speed_of_first_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для первого интервала')
    speed_of_second_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для второго интервала')
    speed_of_third_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для третьего интервала')
    speed_of_fourth_interval = models.CharField(
        max_length=12, choices=OkoDriveStatuses.choices, verbose_name='Статус для четвёртого интервала')

    def __str__(self):
        return f'Настройка статусов для {self.activity_type}'

    class Meta:
        verbose_name = 'Настройка для OkoDrive_status по Activity_type (STILL)'
        verbose_name_plural = 'Настройки для OkoDrive_status по Activity_type (STILL)'
        ordering =['-activity_type']


class SpeedIntervalSettings(models.Model):
    first_interval = models.CharField(max_length=12, verbose_name='Первый интервал')
    second_interval = models.CharField(max_length=12, verbose_name='Второй интервал')
    third_interval = models.CharField(max_length=12, verbose_name='Третий интервал')
    fourth_interval = models.CharField(max_length=12, verbose_name='Четвёртый интервал')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f'Настройка промежутков скоростей для определения OkoDrive_status'

    class Meta:
        verbose_name = 'Настройка промежутков скоростей для определения OkoDrive_status'
        verbose_name_plural = 'Настройки промежутков скоростей для определения OkoDrive_status'
        constraints = [
            UniqueConstraint(fields=['is_main'], condition=Q(is_main=True),
                             name='unique_is_main')
        ]
        ordering = ['-is_main']


class CurrentUTCTime(models.Model):
    current_utc = models.CharField(max_length=2, verbose_name='Текущее значение UTC')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f'UTC {self.current_utc}'



