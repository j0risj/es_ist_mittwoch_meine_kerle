import eimmk
from datetime import datetime as dt
import datetime
import pytz
from pytz import timezone


def test_get_last_wednesday_date():
    day = dt(2020, 9, 16)
    wednesday_before = dt(2020, 9, 9)
    one_day_delta = datetime.timedelta(days = 1)
    assert eimmk.__get_last_wednesday_date(day) == day
    day -= one_day_delta
    assert eimmk.__get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.__get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.__get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.__get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.__get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.__get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.__get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.__get_last_wednesday_date(day) == wednesday_before - datetime.timedelta(days = 7)

def test_is_day_wednesday():
    day = dt(2020, 9, 16)
    assert eimmk.__is_date_wednesday(day) is True
    de_tz = timezone("Europe/Berlin")
    utc_dt = dt(2020, 9, 15, 23, 30, tzinfo=pytz.utc)
    local_time = de_tz.normalize(utc_dt.astimezone(de_tz))
    assert eimmk.__is_date_wednesday(utc_dt) is False
    assert eimmk.__is_date_wednesday(local_time) is True