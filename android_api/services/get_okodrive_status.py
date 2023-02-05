from android_api.models import ActivityTypes, OkoDriveStatuses, BaseOkoDriveSettings, \
    SpeedIntervalSettings, InVehicleOkoDriveSettings, StillOkoDriveSettings, UnknownOkoDriveSettings, \
    OnBicycleOkoDriveSettings, OnFootOkoDriveSettings, WalkingOkoDriveSettings, RunningOkoDriveSettings, \
    TiltingOkoDriveSettings, Device


def make_intervals() -> list:
    speed_intervals_settings = (SpeedIntervalSettings.objects
                                .filter(is_main=True)
                                .values_list('first_interval', 'second_interval', 'third_interval', 'fourth_interval')
                                .first()
                                )

    intervals_list = []
    for speed_interval in speed_intervals_settings:
        interval_data = speed_interval.split(', ')
        if len(interval_data) == 1:
            value_start = value_end = int(interval_data[0])
        else:
            value_start = int(interval_data[0])
            value_end = None if interval_data[1] == 'inf' else int(interval_data[1])
        intervals_list.append([value_start, value_end])

    return intervals_list


def get_index(intervals: list, speed: float) -> int:
    for i, (start, end) in enumerate(intervals):
        if (start < speed or speed == 0) and (end is None or speed <= end):
            return i


def is_equal_speed_interval(current_speed, previous_speed, intervals):
    current_speed_index = get_index(intervals, current_speed)
    previous_speed_index = get_index(intervals, previous_speed)
    return current_speed_index == previous_speed_index


def get_oko_drive_statuses(model, activity_type):
    oko_drive_statuses = (
        model.objects
        .values_list(
            'speed_of_first_interval',
            'speed_of_second_interval',
            'speed_of_third_interval',
            'speed_of_fourth_interval'
        )
        .filter(activity_type=activity_type)
        .first()
    )
    print(model)
    print(oko_drive_statuses)
    return list(oko_drive_statuses)


def get_okodrive_status(activity_type: str, speed: float, **kwargs) -> str:
    print(activity_type)
    print(speed)
    print(kwargs.get('device_id'))
    intervals = make_intervals()
    status_index = get_index(intervals, speed)
    print(status_index)
    models_oko_drive_settings_by_type = {
        'IN_VEHICLE': InVehicleOkoDriveSettings,
        'STILL': StillOkoDriveSettings,
        'UNKNOWN': UnknownOkoDriveSettings,
        'ON_BICYCLE': OnBicycleOkoDriveSettings,
        'ON_FOOT': OnFootOkoDriveSettings,
        'WALKING': WalkingOkoDriveSettings,
        'RUNNING': RunningOkoDriveSettings,
        'TILTING': TiltingOkoDriveSettings,
    }

    model_oko_drive_settings = models_oko_drive_settings_by_type.get(activity_type)
    if not model_oko_drive_settings:
        print(1)
        print(model_oko_drive_settings)
        base_oko_drive_statuses = get_oko_drive_statuses(BaseOkoDriveSettings, activity_type)
        return base_oko_drive_statuses[status_index]

    if not kwargs.get('device_id'):
        print(2)
        print(model_oko_drive_settings)
        oko_drive_statuses = get_oko_drive_statuses(model_oko_drive_settings, ActivityTypes.NONE)
        return oko_drive_statuses[status_index]

    past_device_update = Device.objects.filter(device_id=kwargs.get('device_id')).first()
    if not past_device_update:
        print(3)
        return OkoDriveStatuses.error

    past_device_activity_type = past_device_update.data.activity
    if past_device_activity_type == activity_type and model_oko_drive_settings == StillOkoDriveSettings:
        print(4)
        last_device_history_of_first_interval = Device.objects.filter(
            device_id=kwargs.get('device_id'),
            speed=0
        ).first()
        if last_device_history_of_first_interval and speed == 0:
            return last_device_history_of_first_interval.data.activity
        else:
            return OkoDriveStatuses.ignore
    oko_drive_statuses = get_oko_drive_statuses(model_oko_drive_settings, past_device_activity_type)
    return oko_drive_statuses[status_index]


