# 🔒 RESEARCH BATCH CONFIGURATION v1.0 FINAL V3 - LOCKED
# Batch: TEKB_5m_2024_IS_001 - 144 = 6x6x4
# Lokasi: C:\Users\lenovo\phase1\tekb_core\research_batch_config_v1_locked.py
from typing import Final

RESEARCH_BATCH_ID: Final = "TEKB_5m_2024_IS_001"

canonical_payload: Final = {
    "samson_timeframe_version": "5m_v1.0",
    "entry_definition_version_id": "ENTRY_NEXT_VALID_OPEN_v1.0",
    "b0_selection_rule_version": "B0_SAME_INSTRUMENT_SAME_SLOT_v1.0",
    "mae_mfe_definition_version_id": "MAE_MFE_LONG_ONLY_HIGHLOW_v1.0",
    "atr_definition_version_id": "ATR_5m_Wilder_ResearchEligible_CloseT_v1.0",
    "trading_calendar_version": "IDX_5m_v1.0",
    "bar_validation_version": "BAR_VALIDATION_v1.4",
    "atr": {"period_n": 14, "timeframe": "SAMSON_TIMEFRAME", "atr_entry": "CLOSE_T"},
    "population": {
        "source": "IS_ONLY",
        "type": "B1_SAMSON_ELIGIBLE",
        "is_period": "2024-01-01 to 2024-09-30",
        "min_event_per_instrument": 10,
        "primary_pooling": {"include_all_B1_eligible_events": True},
        "diagnostic_pooling": {"eligibility_action": "EXCLUDE_INSTRUMENTS_BELOW_MIN_EVENT", "min_event_threshold": 10},
    },
    "pooling": {"primary_scheme": "EQUAL_PER_EVENT", "diagnostic_scheme": "EQUAL_PER_INSTRUMENT", "weighting": "NO_MARKET_CAP_WEIGHTING"},
    "grid": {
        "mode": "MODE_A_EXPLICIT",
        "sl_unit": "ATR_MULTIPLE",
        "tp_unit": "ATR_MULTIPLE",
        "sl_grid_atr": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
        "tp_grid_atr": [1.0, 1.5, 2.0, 2.5, 3.0, 4.0],
        "max_hold_bars": ["R1", "R3", "R5", "R10"],
    },
    "grid_validation": {
        "mode": "VALIDATION_ONLY", "enabled": True,
        "mae_distribution": "IS_POOLED_ATR_NORMALIZED",
        "mfe_distribution": "IS_POOLED_ATR_NORMALIZED",
        "percentiles_to_report": [5, 25, 50, 75, 95],
        "purpose": "SANITY_CHECK_ONLY", "buffer_atr": 0.0, "output": "REPORT_ONLY",
    },
    "multiple_testing": {"family_id": "FAMILY_TEKB_5m_2024_IS_001", "correction_method": "BENJAMINI_HOCHBERG_FDR", "expected_count_assertion": 144},
}

batch_metadata: Final = {
    "oos_period": "2024-10-01 to 2024-12-31",
    "is_oos_split_rule": "TIME_BASED",
    "documentation": "Research batch untuk website trading v1.0 - Candidate 144",
}

lock_metadata: Final = {
    "hash_method": "SHA256",
    "configuration_locked_at": "2026-05-13T00:00:00Z",
    "configuration_hash": "", # isi setelah compute
}