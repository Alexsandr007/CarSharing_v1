def get_interval_values_dict(interval_string: str) -> dict:
    interval_values_list = [value for value in interval_string.split(', ')]
    if len(interval_values_list) > 1:
        if 'inf' in interval_values_list:
            interval_values_dict = {
                'identifier': 'infinity',
                'number': int(interval_values_list[0])
            }
        else:
            interval_values_dict = {
                'identifier': 'interval',
                'first_num': interval_values_list[0],
                'second_num': interval_values_list[1]
            }
    else:
        interval_values_dict = {
            'identifier': 'equal',
            'number': int(interval_values_list[0])
        }

    return interval_values_dict
