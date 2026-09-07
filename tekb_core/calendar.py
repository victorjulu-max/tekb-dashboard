
from __future__ import annotations
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .models import CalendarDay, DayType, SessionId
from .constants import LOCAL_TIMEZONE
from .providers import TradingCalendarProvider

class IDXCalendarProvider(TradingCalendarProvider):
    def __init__(self, year, holidays, ramadan_periods, cuti_bersama=None, calendar_version=None):
        self.year=year
        self.holidays=set(holidays)
        if cuti_bersama:
            self.holidays.update(cuti_bersama)
        self.calendar_version=calendar_version or f"IDX-{year}-v1"
        self._ramadan=set()
        for s,e in ramadan_periods:
            cur=datetime.fromisoformat(s)
            end=datetime.fromisoformat(e)
            while cur<=end:
                self._ramadan.add(cur.strftime("%Y-%m-%d"))
                cur+=timedelta(days=1)
    def is_trading_day(self, date):
        if date.weekday()>=5:
            return False
        if date.strftime("%Y-%m-%d") in self.holidays:
            return False
        return True
    def _sessions(self, date):
        ds=date.strftime("%Y-%m-%d")
        if not self.is_trading_day(date):
            return []
        tz=ZoneInfo(LOCAL_TIMEZONE)
        td=date.replace(tzinfo=tz) if date.tzinfo is None else date.astimezone(tz)
        td=td.replace(hour=0,minute=0,second=0,microsecond=0)
        if ds in self._ramadan:
            s1_o=datetime.fromisoformat(f"{ds}T09:00:00").replace(tzinfo=tz)
            s1_c=datetime.fromisoformat(f"{ds}T11:30:00").replace(tzinfo=tz)
            s2_o=datetime.fromisoformat(f"{ds}T14:00:00").replace(tzinfo=tz)
            s2_c=datetime.fromisoformat(f"{ds}T15:00:00").replace(tzinfo=tz)
            return [CalendarDay(td, SessionId.I, s1_o, s1_c, None, None, True, DayType.HALF_DAY_RAMADAN, self.calendar_version), CalendarDay(td, SessionId.II, s2_o, s2_c, None, None, True, DayType.HALF_DAY_RAMADAN, self.calendar_version)]
        else:
            s1_o=datetime.fromisoformat(f"{ds}T09:00:00").replace(tzinfo=tz)
            s1_c=datetime.fromisoformat(f"{ds}T12:00:00").replace(tzinfo=tz)
            b_s=datetime.fromisoformat(f"{ds}T12:00:00").replace(tzinfo=tz)
            b_e=datetime.fromisoformat(f"{ds}T13:30:00").replace(tzinfo=tz)
            s2_o=datetime.fromisoformat(f"{ds}T13:30:00").replace(tzinfo=tz)
            s2_c=datetime.fromisoformat(f"{ds}T15:49:59").replace(tzinfo=tz)
            return [CalendarDay(td, SessionId.I, s1_o, s1_c, b_s, b_e, False, DayType.NORMAL_DAY, self.calendar_version), CalendarDay(td, SessionId.II, s2_o, s2_c, None, None, False, DayType.NORMAL_DAY, self.calendar_version)]
    def session_slots(self, date):
        return self._sessions(date)
    def is_valid_slot(self, ts):
        if ts.tzinfo is None:
            ts=ts.replace(tzinfo=ZoneInfo(LOCAL_TIMEZONE))
        else:
            ts=ts.astimezone(ZoneInfo(LOCAL_TIMEZONE))
        for sl in self._sessions(ts):
            if sl.market_open <= ts <= sl.market_close:
                return True
        return False
