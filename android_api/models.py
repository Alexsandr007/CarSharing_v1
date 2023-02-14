from django.db import models
from django.db.models import UniqueConstraint, Q
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


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


class Parametrs(models.Model):
    value = models.FloatField()
    accuracy = models.FloatField()

    class Meta:
        abstract = True


class Bearing(Parametrs):

    def __str__(self):
        return f'Bearing(id) {self.pk}'

    class Meta:
        verbose_name = 'Bearing'
        verbose_name_plural = 'Bearings'


class Speed(Parametrs):

    def __str__(self):
        return f'Скорость(id) {self.pk}'

    class Meta:
        verbose_name = 'Speed'
        verbose_name_plural = 'Speeds'


class XY(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField()

    def __str__(self):
        return f'Координаты(id) {self.pk}'

    class Meta:
        verbose_name = 'Coordinate'
        verbose_name_plural = 'Coordinates'


class AllActivityMetrics(models.Model):
    activity = models.CharField(max_length=25, choices=ActivityTypes.choices, null=True)
    confidence = models.IntegerField(null=True)

    def __str__(self):
        return f'Метрики активности(id) {self.pk}'

    class Meta:
        verbose_name = 'AllActivityMetric'
        verbose_name_plural = 'AllActivityMetrics'


class Data(models.Model):
    bearing = models.OneToOneField(
        Bearing,
        on_delete=models.CASCADE,
        null=True
    )
    speed = models.OneToOneField(
        Speed,
        on_delete=models.CASCADE,
        null=True
    )
    xy = models.OneToOneField(
        XY,
        on_delete=models.CASCADE,
        null=True
    )
    time = models.CharField(max_length=625, blank=True, verbose_name='Last message')
    custom_utc = models.DateTimeField(auto_now=True)
    activity = models.CharField(max_length=25, null=True)
    all_activity_metrics = models.ManyToManyField(AllActivityMetrics, null=True)

    def __str__(self):
        return f'Информация(id) {self.pk}'

    def last_edited_custom_utc(self):
        utc_settings = CurrentUTCTime.objects.filter(is_main=True).first()
        utc_sign = utc_settings.current_utc[0]
        utc_num = int(utc_settings.current_utc[1])
        last_edited_time = self.custom_utc
        return (last_edited_time - datetime.timedelta(hours=utc_num)).strftime('%Y-%m-%d %H:%M:%S') if utc_sign == '-' \
            else (last_edited_time + datetime.timedelta(hours=utc_num)).strftime('%Y-%m-%d %H:%M:%S')


class Device(models.Model):
    device_id = models.IntegerField()
    data = models.OneToOneField(
        Data,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Телеметрия устройства'
        verbose_name_plural = 'Телеметрия устройств'

    def __str__(self):
        return f'Устройство(id) {self.device_id}'


class CustomUtcHistoricalModel(models.Model):

    custom_utc_history = models.DateTimeField(auto_now=True, null=True)
    def last_edited_custom_utc(self):
        utc_settings = CurrentUTCTime.objects.filter(is_main=True).first()
        utc_sign = utc_settings.current_utc[0]
        utc_num = int(utc_settings.current_utc[1])
        last_edited_time = self.custom_utc_history
        return (last_edited_time - datetime.timedelta(hours=utc_num)).strftime('%Y-%m-%d %H:%M:%S') if utc_sign == '-' \
            else (last_edited_time + datetime.timedelta(hours=utc_num)).strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        abstract = True


class DeviceHistory(models.Model):
    device_id = models.IntegerField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    activity_type = models.CharField(max_length=25, choices=ActivityTypes.choices)
    okodrive_status = models.CharField(
        max_length=25,
        blank=True,
        choices=OkoDriveStatuses.choices,
        default=OkoDriveStatuses.ignore)
    speed = models.DecimalField(max_digits=5, decimal_places=2)
    bearing = models.FloatField()
    history = HistoricalRecords(bases=[CustomUtcHistoricalModel, ])
    time = models.CharField(max_length=625, blank=True, verbose_name='Last message')
    all_activity_metrics = models.CharField(max_length=100, null=True)
    yandex_link = models.CharField(max_length=625, blank=True, null=True)
    custom_utc = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'История устройства'
        verbose_name_plural = 'История устройств'
        ordering = ['-time']

    def __str__(self):
        return f'Устройство {self.device_id}'

    def last_edited_custom_utc(self):
        utc_settings = CurrentUTCTime.objects.filter(is_main=True).first()
        utc_sign = utc_settings.current_utc[0]
        utc_num = int(utc_settings.current_utc[1])
        last_edited_time = self.custom_utc
        return (last_edited_time - datetime.timedelta(hours=utc_num)).strftime('%Y-%m-%d %H:%M:%S') if utc_sign == '-' \
            else (last_edited_time + datetime.timedelta(hours=utc_num)).strftime('%Y-%m-%d %H:%M:%S')




class OkoDriveStatusActive(models.Model):
    device_id = models.CharField(max_length=20, null=True)
    activity_status = models.CharField(max_length=20)

    def __str__(self):
        return f'Статусы активности устройств {self.device_id}'


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
        ordering = ['-activity_type']


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



