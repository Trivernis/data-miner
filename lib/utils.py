import re
from datetime import timedelta

time_regex = re.compile(r'((?P<days>\d+?)[Dd])?((?P<hours>\d+?)[Hh])?((?P<minutes>\d+?)[Mm])?((?P<seconds>\d+?)[Ss])?')


def parse_duration(dur_string: str) -> timedelta:
    """
    Parses the dur_string into a duration in the format <days>d<hours>h<minutes>m<seconds>s.
    Not every value must be present
    :param dur_string:
    :return:
    """
    parts = time_regex.match(dur_string)
    if not parts:
        return timedelta()
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)

    return timedelta(**time_params)
