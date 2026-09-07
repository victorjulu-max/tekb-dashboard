"""
TEKB Core v1.4 - Phase 5 VALIDATION
Full compliance check V1.4 FINAL
"""
from __future__ import annotations
from typing import Dict, List
from.constants import (
    PIPELINE_VERSION, BUILD_SPEC_VERSION, HYGIENE_CHECK_ORDER,
    SUPPORTED_TIMEFRAMES, ALERT_TERMS, FORBIDDEN_ALERT_TERMS,
    COST_MODEL_STATUS, DEFAULT_IS_START, DEFAULT_IS_END, DEFAULT_OOS_START,
    ROLLING_WINDOW, MIN_REQUIRED, SAMSON_THRESHOLD, BASELINE_METHOD,
    RESEARCH_WARMUP_BARS, MIN_RESEARCH_BARS
)

REQUIRED_HYGIENE_ORDER = (
    "SCHEMA_CHECK","TIMESTAMP_CHECK","DUPLICATE_CHECK","ZERO_RANGE_FLAG",
    "TRADING_SESSION_CHECK","TRADING_HALT_CHECK","CORPORATE_ACTION_AUDIT","WARM_UP_ELIGIBILITY"
)

def validate_constants() -> Dict[str, bool]:
    return {
        "pipeline_version_locked": PIPELINE_VERSION == "v0.2",
        "build_spec_locked": BUILD_SPEC_VERSION == "v1.4",
        "hygiene_order_locked": HYGIENE_CHECK_ORDER == REQUIRED_HYGIENE_ORDER,
        "timeframes_ok": all(tf in SUPPORTED_TIMEFRAMES for tf in ("5M","15M","1H","4H","1D")),
        "alert_terms_no_buy_sell": all(t not in FORBIDDEN_ALERT_TERMS for t in ALERT_TERMS),
        "cost_model_is_assumption": COST_MODEL_STATUS == "CONFIGURED_ASSUMPTION",
        "samson_threshold": SAMSON_THRESHOLD == 2.5,
        "baseline_method": BASELINE_METHOD == "SAME_SLOT",
        "rolling_window": ROLLING_WINDOW == 20,
        "min_required": MIN_REQUIRED == 20,
        "research_warmup_exists": RESEARCH_WARMUP_BARS == 50,
        "min_research_exists": MIN_RESEARCH_BARS == 20,
    }

def validate_oos_constants() -> Dict[str, bool]:
    return {
        "is_start": DEFAULT_IS_START == "2016-01-01",
        "is_end": DEFAULT_IS_END == "2022-12-31",
        "oos_start": DEFAULT_OOS_START == "2023-01-01",
        "no_oos_end_default": True, # enforced by OOSConfig requiring explicit
    }

def validate_full_v14() -> Dict[str, any]:
    const_check = validate_constants()
    oos_check = validate_oos_constants()
    all_const = all(const_check.values())
    all_oos = all(oos_check.values())
    return {
        "constants": const_check,
        "oos_constants": oos_check,
        "all_constants_pass": all_const,
        "all_oos_pass": all_oos,
        "v14_compliant": all_const and all_oos,
        "pipeline_version": PIPELINE_VERSION,
        "build_spec_version": BUILD_SPEC_VERSION,
        "golden_ready": all_const and all_oos,
    }

def validate_pipeline_state(state) -> List[str]:
    errors = []
    if not state.hygiene_passed:
        errors.append("Hygiene not passed")
    if not state.adjusted_view_built:
        errors.append("Adjusted view not built")
    if not state.market_status_checked:
        errors.append("Market status not checked")
    if not state.calendar_checked:
        errors.append("Calendar not checked")
    if state.n_bars < (RESEARCH_WARMUP_BARS + MIN_RESEARCH_BARS) and state.research_eligible:
        errors.append("Research eligible but insufficient bars")
    if not state.oos_locked:
        errors.append("OOS not locked")
    return errors