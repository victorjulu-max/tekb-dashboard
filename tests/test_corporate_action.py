
from datetime import datetime
from tekb_core.models import CorporateAction, ActionType, NormalizedBar
from tekb_core.corporate_action import compute_factor, cumulative_factor_for_bar, build_adjusted_view

def test_rights_issue_volume_not_applied():
    action = CorporateAction("CA1","BBCA", ActionType.RIGHTS_ISSUE, datetime(2024,1,3), ratio=0.5, cash_value=5000, source="test", retrieved_at=datetime.now())
    action.__dict__["subscription_price"]=5000
    f = compute_factor(action, 100)
    assert f.adjustment_factor_volume is None

def test_split_factor():
    a = CorporateAction("S1","BBCA", ActionType.SPLIT, datetime(2024,1,5), ratio=2.0, cash_value=None, source="test", retrieved_at=datetime.now())
    f = compute_factor(a, 100)
    assert f.adjustment_factor_price == 0.5
    assert f.adjustment_factor_volume == 2.0

def test_cumulative_independence():
    a1 = CorporateAction("SPLIT1","BBCA", ActionType.SPLIT, datetime(2024,1,5), ratio=2.0, cash_value=None, source="test", retrieved_at=datetime.now())
    a2 = CorporateAction("SPLIT2","BBCA", ActionType.SPLIT, datetime(2024,1,10), ratio=2.0, cash_value=None, source="test", retrieved_at=datetime.now())
    f1 = compute_factor(a1, 100)
    f2 = compute_factor(a2, 200)
    # bar before both
    cum_p, cum_v, ids = cumulative_factor_for_bar(datetime(2024,1,1), [f1,f2])
    assert abs(cum_p - 0.25) < 1e-9
    # bar between
    cum_p_mid, _, _ = cumulative_factor_for_bar(datetime(2024,1,7), [f1,f2])
    assert abs(cum_p_mid - 0.5) < 1e-9
    # bar after both
    cum_p_after, _, _ = cumulative_factor_for_bar(datetime(2024,1,15), [f1,f2])
    assert cum_p_after == 1.0

def test_build_adjusted_view():
    bars = [
        NormalizedBar("BBCA","1D", datetime(2024,1,1), datetime(2024,1,1), 100,110,90,105,1000,"test"),
        NormalizedBar("BBCA","1D", datetime(2024,1,2), datetime(2024,1,2), 100,110,90,106,1000,"test"),
        NormalizedBar("BBCA","1D", datetime(2024,1,6), datetime(2024,1,6), 100,110,90,107,1000,"test"),
    ]
    actions = [
        CorporateAction("S1","BBCA", ActionType.SPLIT, datetime(2024,1,5), ratio=2.0, cash_value=None, source="test", retrieved_at=datetime.now()),
    ]
    view = build_adjusted_view(bars, actions)
    assert len(view) == 3
    assert view[0].adjustment_factor_price == 0.5
    assert view[2].adjustment_factor_price == 1.0
