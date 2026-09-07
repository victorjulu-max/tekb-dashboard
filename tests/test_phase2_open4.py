
from datetime import datetime
from zoneinfo import ZoneInfo
from tekb_core.calendar import IDXCalendarProvider
from tekb_core.models import DayType
from tekb_core.constants import LOCAL_TIMEZONE

def test_idx_normal_day():
    cal = IDXCalendarProvider(2024, ["2024-01-01"], [("2024-03-12","2024-04-10")])
    d = datetime(2024,1,8)
    assert cal.is_trading_day(d)
    slots = cal.session_slots(d)
    assert len(slots)==2
    assert slots[0].day_type == DayType.NORMAL_DAY

def test_idx_holiday_and_weekend():
    cal = IDXCalendarProvider(2024, ["2024-01-01"], [("2024-03-12","2024-04-10")], cuti_bersama=["2024-04-08"])
    assert not cal.is_trading_day(datetime(2024,1,1))
    assert not cal.is_trading_day(datetime(2024,1,6))
    assert not cal.is_trading_day(datetime(2024,4,8))

def test_idx_ramadan_half_day():
    cal = IDXCalendarProvider(2024, [], [("2024-03-12","2024-04-10")])
    slots = cal.session_slots(datetime(2024,3,15))
    assert slots[0].day_type == DayType.HALF_DAY_RAMADAN
    assert slots[0].market_close.hour == 11
    assert slots[1].market_open.hour == 14

def test_idx_valid_slot():
    cal = IDXCalendarProvider(2024, [], [("2024-03-12","2024-04-10")])
    tz = ZoneInfo(LOCAL_TIMEZONE)
    assert cal.is_valid_slot(datetime(2024,1,8,10,0,tzinfo=tz))
    assert not cal.is_valid_slot(datetime(2024,1,8,12,30,tzinfo=tz))

def test_idx_calendar_version():
    cal = IDXCalendarProvider(2024, [], [("2024-03-12","2024-04-10")], calendar_version="IDX-2024-Ramadan-v2")
    assert cal.calendar_version == "IDX-2024-Ramadan-v2"
