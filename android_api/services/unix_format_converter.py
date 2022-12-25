import datetime


def unix_converter(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S')
