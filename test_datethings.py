import eimmk
from datetime import datetime as dt
import datetime

def test_get_last_wednesday_date():
    day = dt(2020, 9, 16)
    wednesday_before = dt(2020, 9, 9)
    one_day_delta = datetime.timedelta(days = 1)
    assert eimmk.get_last_wednesday_date(day) == day
    day -= one_day_delta
    assert eimmk.get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.get_last_wednesday_date(day) == wednesday_before
    day -= one_day_delta
    assert eimmk.get_last_wednesday_date(day) == wednesday_before - datetime.timedelta(days = 7)

def test_is_day_wednesday():
    day = day = dt(2020, 9, 16)
    assert eimmk.is_date_wednesday(day) is True