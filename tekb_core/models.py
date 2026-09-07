"""
Core data models for TEKB Stock Analyzer (tekb_core).

These are plain, framework-independent dataclasses/enums shared by the
laptop research engine and the Vercel operational service. Neither side
should redefine these — import them from here.

Status enums encode the state machines from the Technical Build
Specification v1.3. Adding a new value to any of these enums is a
methodological decision, not a coding one — flag it as OPEN first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Enums / status machines
# ---------------------------------------------------------------------------

class BarValidationStatus(str, Enum):
    VALID = "VALID"
    EXCLUDED = "EXCLUDED"


class DataGapStatus(str, Enum):
    """A data gap is an anomaly, not a bar (§12)."""
    NONE = "NONE"
    SUSPECTED_GAP = "SUSPECTED_GAP"
    CONFIRMED_HALT = "CONFIRMED_HALT"


class DayType(str, Enum):
    NORMAL_DAY = "NORMAL_DAY"
    HOLIDAY = "HOLIDAY"
    HALF_DAY_RAMADAN = "HALF_DAY_RAMADAN"
    SPECIAL_HALF_DAY = "SPECIAL_HALF_DAY"


class SessionId(str, Enum):
    I = "I"
    II = "II"


class MarketStatus(str, Enum):
    NORMAL = "NORMAL"
    HALTED = "HALTED"
    SUSPENDED = "SUSPENDED"
    RESUMED = "RESUMED"
    SPECIAL_SESSION = "SPECIAL_SESSION"


class CorporateActionAuditStatus(str, Enum):
    PENDING = "PENDING"
    AUDITED_NO_ACTION = "AUDITED_NO_ACTION"
    AUDITED_WITH_ACTION = "AUDITED_WITH_ACTION"


class ActionType(str, Enum):
    SPLIT = "SPLIT"
    REVERSE_SPLIT = "REVERSE_SPLIT"
    DIVIDEND = "DIVIDEND"
    RIGHTS_ISSUE = "RIGHTS_ISSUE"
    BONUS_SHARE = "BONUS_SHARE"


class AdjustmentMethod(str, Enum):
    SPLIT_RATIO = "SPLIT_RATIO"
    DIVIDEND_CASH = "DIVIDEND_CASH"
    RIGHTS_RATIO = "RIGHTS_RATIO"
    BONUS_RATIO = "BONUS_RATIO"


class AdjustmentStatus(str, Enum):
    NOT_ADJUSTED = "NOT_ADJUSTED"
    ADJUSTED = "ADJUSTED"


class WarmupStatus(str, Enum):
    WARMUP = "WARMUP"
    INSUFFICIENT_BASELINE = "INSUFFICIENT_BASELINE"
    READY = "READY"


class SamsonDirection(str, Enum):
    SAMSON_PLUS = "SAMSON+"
    SAMSON_MINUS = "SAMSON-"


class EntryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"


class HypothesisStatus(str, Enum):
    DRAFT = "DRAFT"
    LOCKED = "LOCKED"


class ResearchBatchStatus(str, Enum):
    OPEN = "OPEN"
    FDR_EVALUATED = "FDR_EVALUATED"
    CLOSED = "CLOSED"


class MultipleTestingStatus(str, Enum):
    EXPLORATORY = "EXPLORATORY"
    CANDIDATE = "CANDIDATE"
    HYPOTHESIS_LOCK = "HYPOTHESIS_LOCK"
    TESTED = "TESTED"
    OOS_VALIDATED = "OOS_VALIDATED"


class AlertStatus(str, Enum):
    DETECTED = "DETECTED"
    WATCH = "WATCH"
    POTENTIAL_EDGE = "POTENTIAL_EDGE"
    TESTED = "TESTED"
    OOS_VALIDATED = "OOS_VALIDATED"
    PROVEN = "PROVEN"


class HistoricalAlertStatus(str, Enum):
    DETECTED_UNAUDITED = "DETECTED_UNAUDITED"


# ---------------------------------------------------------------------------
# RAW / NORMALIZED (§1, §2, §4.1)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RawBar:
    """Immutable. Exactly as received from the provider. Never mutate."""
    symbol: str
    timeframe: str
    provider_timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    raw_payload: Any
    fetched_at: datetime


@dataclass(frozen=True)
class NormalizedBar:
    """Standard internal representation. RAW must never be overwritten."""
    symbol: str
    timeframe: str
    timestamp_utc: datetime
    timestamp_local: datetime  # Asia/Jakarta
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str


# ---------------------------------------------------------------------------
# Corporate actions (§6, §7)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CorporateAction:
    action_id: str
    symbol: str
    action_type: ActionType
    ex_date: datetime
    ratio: Optional[float]
    cash_value: Optional[float]
    source: str
    retrieved_at: datetime


@dataclass(frozen=True)
class AdjustedBar:
    """Derived view. RAW/NORMALIZED are untouched — this is a separate layer.
    V1.4: adjustment_factor_volume=None means NOT_APPLIED for RIGHTS_ISSUE."""
    normalized: NormalizedBar
    corporate_action_id: Optional[str]
    adjustment_method: Optional[AdjustmentMethod]
    adjustment_factor_price: float
    adjustment_factor_volume: Optional[float]  # None = NOT_APPLIED for RIGHTS_ISSUE (V1.4 Fix #1)
    adjustment_status: AdjustmentStatus


# ---------------------------------------------------------------------------
# Trading calendar (§9)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CalendarDay:
    trading_date: datetime
    session_id: SessionId
    market_open: datetime
    market_close: datetime
    break_start: Optional[datetime]
    break_end: Optional[datetime]
    is_half_day: bool
    day_type: DayType
    calendar_version: str


# ---------------------------------------------------------------------------
# Bar validation / gap anomaly (§12) — kept as two separate concepts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BarValidationResult:
    bar: NormalizedBar
    status: BarValidationStatus
    reason: Optional[str] = None


@dataclass(frozen=True)
class GapAnomalyRecord:
    """A gap is recorded as an anomaly, never fabricated as a bar."""
    symbol: str
    timeframe: str
    gap_start: datetime
    gap_end: datetime
    status: DataGapStatus
    detected_at: datetime
    confirmed_by: Optional[str] = None  # e.g. MarketStatusProvider source


# ---------------------------------------------------------------------------
# SAMSON event (§16, §17, §24)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SamsonEvent:
    event_id: str
    symbol: str
    timeframe: str
    timestamp_utc: datetime
    direction: SamsonDirection
    volume: float
    baseline_volume: float
    rv: float  # relative volume = volume / baseline_volume
    price: float
    research_eligible: bool
    corporate_action_status: CorporateActionAuditStatus
    is_independent: bool
    cluster_id: str
    dataset_snapshot_id: str
    specification_id: str


# ---------------------------------------------------------------------------
# Research ledger entry (§24-26)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResearchLedgerEntry:
    event: SamsonEvent
    exclusion_reason: Optional[str]
    entry_status: EntryStatus
    supersedes_event_id: Optional[str]
    superseded_by_event_id: Optional[str]
    correction_reason: Optional[str]
    correction_timestamp: Optional[datetime]
    cost_model_id: str
    multiple_testing_family_id: Optional[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Research Batch (§11.0 V1.4) - anti-circularity fix
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResearchBatch:
    """V1.4 FIX #3: created BEFORE any hypothesis. Holds EXPLORATORY configs.
    research_batch_id is the identity for multiple_testing_family."""
    research_batch_id: str
    test_configurations: tuple  # list of research config dicts
    status: ResearchBatchStatus
    created_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Hypothesis / B0-B1 (§30)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResearchHypothesis:
    research_batch_id: str  # V1.4 FIX #3: FK -> ResearchBatch (mandatory)
    hypothesis_id: str
    b0_definition: str
    b1_definition: str
    oos_start: datetime
    oos_end: datetime  # must be an explicit absolute date once LOCKED
    locked_at: Optional[datetime]
    universe: tuple
    status: HypothesisStatus


# ---------------------------------------------------------------------------
# Dataset snapshot (§27) and specification version/fingerprint (§28-29)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DatasetSnapshot:
    dataset_snapshot_id: str
    ohlcv_version: str
    corporate_action_version: str
    calendar_version: str
    provider_source_name: str
    download_timestamp: datetime
    snapshot_manifest_hash: str
    universe: tuple
    timeframe: str
    start_date: datetime
    end_date: datetime
    row_count: int
    content_hash: str


@dataclass(frozen=True)
class SpecificationVersion:
    specification_id: str       # database identity — NOT the raw hash
    fingerprint_hash: str        # immutable fingerprint (SHA-256)
    data_version: str
    calendar_version: str
    corporate_action_version: str
    pipeline_version: str
    detector_version: str
    parameter_version: str


@dataclass(frozen=True)
class CostModel:
    cost_model_id: str
    fee_pct: float
    slippage_pct: float
    status: str = "CONFIGURED_ASSUMPTION"
