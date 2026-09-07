
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence
from .models import ActionType, AdjustmentMethod, AdjustmentStatus, AdjustedBar, CorporateAction, NormalizedBar

@dataclass(frozen=True)
class FactorResult:
    corporate_action_id: str
    adjustment_method: AdjustmentMethod
    adjustment_factor_price: float
    adjustment_factor_volume: Optional[float]
    ex_date: datetime

def _find_close_prior_ex_date(bars_sorted, ex_date):
    prior = [b for b in bars_sorted if b.timestamp_local < ex_date or b.timestamp_utc < ex_date]
    if not prior:
        raise ValueError(f"No prior bar before {ex_date}")
    return prior[-1].close

def compute_factor(action, close_prior):
    from .models import AdjustmentMethod
    if action.action_type in (ActionType.SPLIT, ActionType.REVERSE_SPLIT, ActionType.BONUS_SHARE):
        method = AdjustmentMethod.SPLIT_RATIO if action.action_type != ActionType.BONUS_SHARE else AdjustmentMethod.BONUS_RATIO
        return FactorResult(action.action_id, method, 1.0/action.ratio, action.ratio, action.ex_date)
    elif action.action_type == ActionType.DIVIDEND:
        return FactorResult(action.action_id, AdjustmentMethod.DIVIDEND_CASH, (close_prior - action.cash_value)/close_prior, 1.0, action.ex_date)
    elif action.action_type == ActionType.RIGHTS_ISSUE:
        sub = getattr(action, "subscription_price", None) or action.cash_value
        terp = (close_prior + (action.ratio * sub)) / (1.0 + action.ratio)
        return FactorResult(action.action_id, AdjustmentMethod.RIGHTS_RATIO, terp/close_prior, None, action.ex_date)
    else:
        raise ValueError("Unsupported")

def cumulative_factor_for_bar(bar_ts, factors):
    relevant = [f for f in factors if f.ex_date > bar_ts]
    if not relevant:
        return 1.0, 1.0, []
    cum_p = 1.0
    ids=[]
    vol_none=False
    cum_v=1.0
    has_v=False
    for f in relevant:
        cum_p*=f.adjustment_factor_price
        ids.append(f.corporate_action_id)
        if f.adjustment_factor_volume is None:
            vol_none=True
        else:
            cum_v*=f.adjustment_factor_volume
            has_v=True
    return cum_p, (None if vol_none else (cum_v if has_v else 1.0)), ids

def build_adjusted_view(normalized_bars, corporate_actions):
    bars_sorted = sorted(normalized_bars, key=lambda b: b.timestamp_utc)
    factors=[]
    for a in sorted(corporate_actions, key=lambda a: a.ex_date, reverse=True):
        cp=_find_close_prior_ex_date(bars_sorted, a.ex_date)
        factors.append(compute_factor(a, cp))
    adj=[]
    for bar in bars_sorted:
        cum_p, cum_v, ids = cumulative_factor_for_bar(bar.timestamp_utc, factors)
        if cum_p==1.0 and (cum_v==1.0 or (cum_v is None and not ids)):
            adj.append(AdjustedBar(bar, None, None, 1.0, 1.0, AdjustmentStatus.NOT_ADJUSTED))
        else:
            rel=[f for f in factors if f.ex_date>bar.timestamp_utc]
            method=rel[0].adjustment_method if rel else None
            ca_id=",".join(ids) if ids else None
            fv = cum_v if cum_v is not None else None
            # store 1.0 as placeholder if None for legacy float field but models now Optional
            adj.append(AdjustedBar(bar, ca_id, method, cum_p, fv, AdjustmentStatus.ADJUSTED))
    return adj
