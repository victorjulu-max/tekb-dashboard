
from datetime import datetime, timezone
from tekb_core.models import MarketStatus, DataGapStatus
from tekb_core.providers import (
    CSVMarketStatusProvider, ManualMarketStatusProvider, BrokerMarketStatusProvider,
    CompositeMarketStatusProvider, confirm_gap_with_provider
)
from tekb_core.hygiene import detect_gap
import tempfile, csv, os

def test_csv_market_status_halted():
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["symbol","timestamp","status","source","confirmed_by"])
        w.writeheader()
        w.writerow({"symbol":"BBCA","timestamp":"2024-01-05T10:00:00+00:00","status":"HALTED","source":"bei","confirmed_by":"bei_api"})
        w.writerow({"symbol":"BBCA","timestamp":"2024-01-05T11:00:00+00:00","status":"NORMAL","source":"bei","confirmed_by":"bei_api"})
    provider = CSVMarketStatusProvider(path)
    st1 = provider.status_at("BBCA", datetime(2024,1,5,10,30,tzinfo=timezone.utc))
    assert st1 == MarketStatus.HALTED
    st2 = provider.status_at("BBCA", datetime(2024,1,5,11,30,tzinfo=timezone.utc))
    assert st2 == MarketStatus.NORMAL
    st_unknown = provider.status_at("BBRI", datetime(2024,1,5,10,30,tzinfo=timezone.utc))
    assert st_unknown == MarketStatus.NORMAL  # default NORMAL when no record
    os.unlink(path)

def test_manual_market_status_provider():
    statuses = [
        ("BBCA", datetime(2024,1,5,10,0,tzinfo=timezone.utc), MarketStatus.SUSPENDED),
        ("BBCA", datetime(2024,1,5,12,0,tzinfo=timezone.utc), MarketStatus.RESUMED),
    ]
    p = ManualMarketStatusProvider(statuses)
    assert p.status_at("BBCA", datetime(2024,1,5,11,0,tzinfo=timezone.utc)) == MarketStatus.SUSPENDED
    assert p.status_at("BBCA", datetime(2024,1,5,13,0,tzinfo=timezone.utc)) == MarketStatus.RESUMED

def test_broker_market_status_stub():
    p = BrokerMarketStatusProvider()
    try:
        p.status_at("BBCA", datetime(2024,1,5,10,0,tzinfo=timezone.utc))
        assert False
    except NotImplementedError as e:
        assert "CSV manual fallback" in str(e) or "not implemented" in str(e).lower()

def test_composite_market_status_precedence():
    # csv says HALTED, manual says NORMAL — composite should return HALTED (halt takes precedence)
    p_halt = ManualMarketStatusProvider([("BBCA", datetime(2024,1,5,9,0,tzinfo=timezone.utc), MarketStatus.HALTED)])
    p_normal = ManualMarketStatusProvider([("BBCA", datetime(2024,1,5,9,0,tzinfo=timezone.utc), MarketStatus.NORMAL)])
    comp = CompositeMarketStatusProvider([p_normal, p_halt])
    st = comp.status_at("BBCA", datetime(2024,1,5,10,0,tzinfo=timezone.utc))
    assert st == MarketStatus.HALTED

def test_suspected_gap_vs_confirmed_halt_separation():
    # V1.4 §13-14: gap alone must NOT be assumed as halt — requires explicit provider evidence
    prev = datetime(2024,1,5,10,0,tzinfo=timezone.utc)
    cur = datetime(2024,1,5,11,0,tzinfo=timezone.utc)
    gap = detect_gap("BBCA","5M", prev, cur)
    assert gap is not None
    assert gap.status == DataGapStatus.SUSPECTED_GAP  # not CONFIRMED_HALT yet

    # Without halt evidence -> remains SUSPECTED_GAP
    p_normal = ManualMarketStatusProvider([])
    confirmed = confirm_gap_with_provider(gap, p_normal)
    assert confirmed.status == DataGapStatus.SUSPECTED_GAP

    # With halt evidence -> CONFIRMED_HALT
    p_halt = ManualMarketStatusProvider([("BBCA", datetime(2024,1,5,9,0,tzinfo=timezone.utc), MarketStatus.HALTED)])
    confirmed2 = confirm_gap_with_provider(gap, p_halt)
    assert confirmed2.status == DataGapStatus.CONFIRMED_HALT
    assert confirmed2.confirmed_by == p_halt.source_name

def test_holiday_not_misinterpreted_as_anomaly():
    # IDX holiday should be NORMAL in market status, gap remains SUSPECTED_GAP, not promoted to halt
    # This ensures we don't misinterpret holidays as price anomalies per your requirement
    p_normal = ManualMarketStatusProvider([])
    gap = detect_gap("BBCA","5M", datetime(2024,1,1,10,0,tzinfo=timezone.utc), datetime(2024,1,2,10,0,tzinfo=timezone.utc))
    # gap detected
    assert gap.status == DataGapStatus.SUSPECTED_GAP
    # but not confirmed as halt without evidence
    confirmed = confirm_gap_with_provider(gap, p_normal)
    assert confirmed.status == DataGapStatus.SUSPECTED_GAP
    assert confirmed.confirmed_by is None
