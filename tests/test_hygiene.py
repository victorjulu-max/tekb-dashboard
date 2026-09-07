
from datetime import datetime
from tekb_core.models import NormalizedBar, CorporateActionAuditStatus, MarketStatus
from tekb_core.hygiene import DataHygieneEngine, detect_gap, confirm_gap
from tekb_core.providers import TradingCalendarProvider, MarketStatusProvider
from tekb_core.constants import HYGIENE_CHECK_ORDER

class DummyCalendar(TradingCalendarProvider):
    def is_trading_day(self, date): return True
    def session_slots(self, date): return []
    def is_valid_slot(self, ts): return True

class DummyMarket(MarketStatusProvider):
    def status_at(self, symbol, ts): return MarketStatus.NORMAL

class HaltMarket(MarketStatusProvider):
    def status_at(self, symbol, ts): return MarketStatus.HALTED

def make_bar():
    return NormalizedBar("BBCA","1D", datetime(2024,1,2,3,0), datetime(2024,1,2,10,0), 100,110,90,105,1000,"test")

def test_hygiene_order_locked():
    assert HYGIENE_CHECK_ORDER == ("SCHEMA_CHECK","TIMESTAMP_CHECK","DUPLICATE_CHECK","ZERO_RANGE_FLAG","TRADING_SESSION_CHECK","TRADING_HALT_CHECK","CORPORATE_ACTION_AUDIT","WARM_UP_ELIGIBILITY")

def test_schema_check():
    engine = DataHygieneEngine(DummyCalendar(), DummyMarket(), lambda s,t: CorporateActionAuditStatus.AUDITED_NO_ACTION, lambda s,tf,ts: True)
    bar = make_bar()
    res = engine.run(bar, ("symbol","nonexistent_field"))
    assert res.failed_step == "SCHEMA_CHECK"

def test_timestamp_check():
    engine = DataHygieneEngine(DummyCalendar(), DummyMarket(), lambda s,t: CorporateActionAuditStatus.AUDITED_NO_ACTION, lambda s,tf,ts: True)
    bar = NormalizedBar("BBCA","1D", None, None, 100,110,90,105,1000,"test")
    res = engine.run(bar, ("symbol","timeframe"))
    assert res.failed_step == "TIMESTAMP_CHECK"

def test_trading_session_check():
    class BadCal(DummyCalendar):
        def is_valid_slot(self, ts): return False
    engine = DataHygieneEngine(BadCal(), DummyMarket(), lambda s,t: CorporateActionAuditStatus.AUDITED_NO_ACTION, lambda s,tf,ts: True)
    res = engine.run(make_bar(), ("symbol","timeframe"))
    assert res.failed_step == "TRADING_SESSION_CHECK"

def test_trading_halt_check():
    engine = DataHygieneEngine(DummyCalendar(), HaltMarket(), lambda s,t: CorporateActionAuditStatus.AUDITED_NO_ACTION, lambda s,tf,ts: True)
    res = engine.run(make_bar(), ("symbol","timeframe"))
    assert res.failed_step == "TRADING_HALT_CHECK"

def test_corporate_action_audit_pending():
    engine = DataHygieneEngine(DummyCalendar(), DummyMarket(), lambda s,t: CorporateActionAuditStatus.PENDING, lambda s,tf,ts: True)
    res = engine.run(make_bar(), ("symbol","timeframe"))
    assert res.failed_step == "CORPORATE_ACTION_AUDIT"
    assert not res.research_eligible

def test_warmup_eligibility():
    engine = DataHygieneEngine(DummyCalendar(), DummyMarket(), lambda s,t: CorporateActionAuditStatus.AUDITED_NO_ACTION, lambda s,tf,ts: False)
    res = engine.run(make_bar(), ("symbol","timeframe"))
    assert res.failed_step == "WARM_UP_ELIGIBILITY"

def test_research_eligible_true():
    engine = DataHygieneEngine(DummyCalendar(), DummyMarket(), lambda s,t: CorporateActionAuditStatus.AUDITED_NO_ACTION, lambda s,tf,ts: True)
    res = engine.run(make_bar(), ("symbol","timeframe"))
    assert res.research_eligible
    assert res.failed_step is None

def test_gap_detection():
    prev = datetime(2024,1,2,10,0)
    cur = datetime(2024,1,2,10,30)
    gap = detect_gap("BBCA","5M", prev, cur)
    assert gap is not None
    assert gap.status.value == "SUSPECTED_GAP"

def test_gap_not_bar():
    # gap should not create synthetic bar
    prev = datetime(2024,1,2,10,0)
    cur = datetime(2024,1,2,10,6)
    gap = detect_gap("BBCA","5M", prev, cur)
    assert gap is None
