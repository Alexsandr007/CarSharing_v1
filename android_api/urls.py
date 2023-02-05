from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from android_api.views import DeviceViewSet

router = routers.SimpleRouter()
router.register('telemetry', DeviceViewSet, basename='telemetry')

urlpatterns = [
    # path('get_settings/', TimeStampSettingView.as_view(), name='get_settings'),
]


urlpatterns += router.urls
