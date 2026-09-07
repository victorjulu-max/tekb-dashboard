
from datetime import datetime, timezone
from tekb_core.models import CorporateAction, ActionType, NormalizedBar
from tekb_core.providers import CSVCorporateActionProvider, ManualCorporateActionProvider, YahooCorporateActionProvider, BrokerCorporateActionProvider, CompositeCorporateActionProvider
from tekb_core.corporate_action import build_adjusted_view, compute_factor
import tempfile, csv, os

def test_csv_corporate_action_rights_issue_not_applied():
    # create temp CSV with rights issue
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["action_id","symbol","action_type","ex_date","ratio","cash_value","subscription_price","source"])
        w.writeheader()
        w.writerow({"action_id":"CA1","symbol":"BBCA","action_type":"RIGHTS_ISSUE","ex_date":"2024-01-05T00:00:00","ratio":"0.5","cash_value":"","subscription_price":"5000","source":"test"})
    provider = CSVCorporateActionProvider(path)
    actions = provider.fetch_actions("BBCA", datetime(2024,1,1,tzinfo=timezone.utc), datetime(2024,1,10,tzinfo=timezone.utc))
    assert len(actions)==1
    assert actions[0].action_type==ActionType.RIGHTS_ISSUE
    f = compute_factor(actions[0], 10000)
    assert f.adjustment_factor_volume is None  # NOT_APPLIED per V1.4 Fix #1
    os.unlink(path)

def test_manual_corporate_action_provider_sorted():
    a1 = CorporateAction("A2","BBCA", ActionType.SPLIT, datetime(2024,1,10,tzinfo=timezone.utc), 2.0, None, "test", datetime.now(timezone.utc))
    a2 = CorporateAction("A1","BBCA", ActionType.SPLIT, datetime(2024,1,5,tzinfo=timezone.utc), 2.0, None, "test", datetime.now(timezone.utc))
    p = ManualCorporateActionProvider([a1,a2])
    acts = p.fetch_actions("BBCA", datetime(2024,1,1,tzinfo=timezone.utc), datetime(2024,1,15,tzinfo=timezone.utc))
    assert acts[0].ex_date < acts[1].ex_date

def test_yahoo_corporate_action_mvp():
    p = YahooCorporateActionProvider()
    assert p.source_name == "yahoo_corporate_action"
    # without yfinance, returns []
    acts = p.fetch_actions("BBCA", datetime(2024,1,1,tzinfo=timezone.utc), datetime(2024,1,2,tzinfo=timezone.utc))
    assert isinstance(acts, list)

def test_broker_corporate_action_stub():
    p = BrokerCorporateActionProvider()
    try:
        p.fetch_actions("BBCA", datetime(2024,1,1,tzinfo=timezone.utc), datetime(2024,1,2,tzinfo=timezone.utc))
        assert False
    except NotImplementedError as e:
        assert "CSV fallback" in str(e) or "not implemented" in str(e).lower()

def test_composite_dedup():
    a1 = CorporateAction("A1","BBCA", ActionType.SPLIT, datetime(2024,1,5,tzinfo=timezone.utc), 2.0, None, "test", datetime.now(timezone.utc))
    a2 = CorporateAction("A1_dup","BBCA", ActionType.SPLIT, datetime(2024,1,5,tzinfo=timezone.utc), 2.0, None, "test", datetime.now(timezone.utc))
    p1 = ManualCorporateActionProvider([a1])
    p2 = ManualCorporateActionProvider([a2])
    comp = CompositeCorporateActionProvider([p1,p2])
    acts = comp.fetch_actions("BBCA", datetime(2024,1,1,tzinfo=timezone.utc), datetime(2024,1,10,tzinfo=timezone.utc))
    assert len(acts)==1  # deduped

def test_adjusted_view_with_provider_actions():
    bars = [
        NormalizedBar("BBCA","1D", datetime(2024,1,1,tzinfo=timezone.utc), datetime(2024,1,1,tzinfo=timezone.utc), 100,110,90,105,1000,"test"),
        NormalizedBar("BBCA","1D", datetime(2024,1,6,tzinfo=timezone.utc), datetime(2024,1,6,tzinfo=timezone.utc), 100,110,90,106,1000,"test"),
    ]
    a = CorporateAction("S1","BBCA", ActionType.SPLIT, datetime(2024,1,5,tzinfo=timezone.utc), 2.0, None, "test", datetime.now(timezone.utc))
    view = build_adjusted_view(bars, [a])
    assert view[0].adjustment_factor_price == 0.5
    assert view[1].adjustment_factor_price == 1.0
