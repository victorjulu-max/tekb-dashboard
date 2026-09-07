"""
Locked constants from TEKB Technical Build Specification v1.4 FINAL / CODING-FROZEN.

Do NOT change these values here to "tune" results. Any change to a value
in this file changes `parameter_version` in specification.py and therefore
produces a NEW specification_id / fingerprint_hash (see §28-29 of the spec).

If a parameter needs to change for research purposes, that is a
methodological decision — not a coding decision. Record it as an
OPEN / IMPLEMENTATION QUESTION and get it decided at the Pipeline
Specification / TEKB Definition level first.
"""

from __future__ import annotations

# --- Timezone / calendar -----------------------------------------------
LOCAL_TIMEZONE = "Asia/Jakarta"

# --- Warm-up (§15) -------------------------------------------------------
ROLLING_WINDOW = 20
MIN_REQUIRED = 20

# --- SAMSON Engine (§16) --------------------------------------------------
SAMSON_THRESHOLD = 2.5
BASELINE_METHOD = "SAME_SLOT"
FORWARD_HORIZONS = (1, 3, 5, 10)  # t+1, t+3, t+5, t+10

# --- Declustering (§17) ----------------------------------------------------
DECLUSTER_METHOD = "max_forward_horizon"
DECLUSTER_GAP_CANDLES = 10

# --- Gap detection (§13) ----------------------------------------------------
GAP_THRESHOLD_MULTIPLIER = 3  # gap_threshold = 3 x timeframe_duration

# --- Transaction cost (§32) — CONFIGURED ASSUMPTION, not a market fact ------
FEE_PCT_PER_SIDE = 0.0015
SLIPPAGE_PCT_PER_SIDE = 0.0005
COST_MODEL_STATUS = "CONFIGURED_ASSUMPTION"

# --- Multiple testing (§35) --------------------------------------------------
MULTIPLE_TESTING_CORRECTION_METHOD = "BH"
DEFAULT_FALSE_DISCOVERY_RATE = 0.10

# --- OOS (§36) -----------------------------------------------------------
DEFAULT_IS_START = "2016-01-01"
DEFAULT_IS_END = "2022-12-31"
DEFAULT_OOS_START = "2023-01-01"
# OOS_END has no default: it must be an explicit, locked, absolute date
# supplied at hypothesis-lock time. Do not default this to "today".

# --- Data hygiene engine order (§11) — LOCKED, do not reorder -------------
HYGIENE_CHECK_ORDER = (
    "SCHEMA_CHECK",
    "TIMESTAMP_CHECK",
    "DUPLICATE_CHECK",
    "ZERO_RANGE_FLAG",
    "TRADING_SESSION_CHECK",
    "TRADING_HALT_CHECK",
    "CORPORATE_ACTION_AUDIT",
    "WARM_UP_ELIGIBILITY",
)

# --- Specification / pipeline versions ------------------------------------
PIPELINE_VERSION = "v0.2"          # frozen, methodology layer
BUILD_SPEC_VERSION = "v1.4"        # frozen, coding layer

# --- Minimum timeframes (§43) ----------------------------------------------
SUPPORTED_TIMEFRAMES = ("5M", "15M", "1H", "4H", "1D")

# --- Alert terminology (§19) — BUY/SELL are forbidden -----------------------
ALERT_TERMS = ("DETECTED", "WATCH", "POTENTIAL_EDGE", "TESTED", "OOS_VALIDATED", "PROVEN")
FORBIDDEN_ALERT_TERMS = ("BUY", "SELL")
