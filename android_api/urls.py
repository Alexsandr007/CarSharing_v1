from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from android_api.views import TimeStampSettingView, DeviceViewSet, RegisterDriverView, CheckTelegramAuthView, TelegramConfirmationView, TelegramUntieView

router = routers.SimpleRouter()
router.register('telemetry', DeviceViewSet, basename='telemetry')

urlpatterns = [
    path('get_settings/', TimeStampSettingView.as_view(), name='get_settings'),
    path('reg_driver/', RegisterDriverView.as_view(), name='reg_driver'),
    path('reg_check/<int:device_id>/', CheckTelegramAuthView.as_view(), name='reg_check'),
    path('reg_confirmation/', TelegramConfirmationView.as_view(), name='reg_confirmation'),
    path('untie_telegram/', TelegramUntieView.as_view(), name='untie_telegram')
]


urlpatterns += router.urls
