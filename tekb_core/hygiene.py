"""
Data Hygiene Engine (§11, §12, §13, §14).

The check order below is LOCKED by the spec — do not reorder, skip, or
merge steps:

    1. SCHEMA CHECK
    2. TIMESTAMP CHECK
    3. DUPLICATE CHECK
    4. ZERO-RANGE FLAG
    5. TRADING SESSION CHECK
    6. TRADING HALT CHECK
    7. CORPORATE ACTION AUDIT
    8. WARM-UP ELIGIBILITY

A data gap is NEVER represented as a bar (§12). Gaps are recorded as
GapAnomalyRecord objects, entirely separate from BarValidationResult.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from .constants import GAP_THRESHOLD_MULTIPLIER, HYGIENE_CHECK_ORDER
from .models import (
    BarValidationResult,
    BarValidationStatus,
    CorporateActionAuditStatus,
    DataGapStatus,
    GapAnomalyRecord,
    MarketStatus,
    NormalizedBar,
)
from .providers import MarketStatusProvider, TradingCalendarProvider

TIMEFRAME_MINUTES = {
    "5M": 5,
    "15M": 15,
    "1H": 60,
    "4H": 240,
    "1D": 60 * 24,
}


@dataclass
class HygieneResult:
    """Output of running the full LOCKED-order pipeline over one bar."""
    bar_result: BarValidationResult
    corporate_action_status: CorporateActionAuditStatus
    research_eligible: bool
    failed_step: Optional[str] = None


class DataHygieneEngine:
    """Runs the 8-step LOCKED check order against a single normalized bar.

    Corporate-action auditing and warm-up eligibility are deliberately
    left as injected callables/providers rather than hardcoded here,
    since their concrete sources are OPEN items (see providers.py).
    """

    def __init__(
        self,
        calendar_provider: TradingCalendarProvider,
        market_status_provider: MarketStatusProvider,
        corporate_action_audit_lookup,  # Callable[[str, datetime], CorporateActionAuditStatus]
        warmup_check,  # Callable[[str, str, datetime], bool] -> True if READY
    ):
        self._calendar = calendar_provider
        self._market_status = market_status_provider
        self._ca_audit_lookup = corporate_action_audit_lookup
        self._warmup_check = warmup_check
        assert HYGIENE_CHECK_ORDER[0] == "SCHEMA_CHECK"  # order sanity guard

    def run(self, bar: NormalizedBar, expected_schema_fields: tuple[str, ...]) -> HygieneResult:
        # 1. SCHEMA CHECK
        for field_name in expected_schema_fields:
            if not hasattr(bar, field_name):
                return HygieneResult(
                    bar_result=BarValidationResult(bar, BarValidationStatus.EXCLUDED, "schema_mismatch"),
                    corporate_action_status=CorporateActionAuditStatus.PENDING,
                    research_eligible=False,
                    failed_step="SCHEMA_CHECK",
                )

        # 2. TIMESTAMP CHECK
        if bar.timestamp_utc is None or bar.timestamp_local is None:
            return HygieneResult(
                bar_result=BarValidationResult(bar, BarValidationStatus.EXCLUDED, "missing_timestamp"),
                corporate_action_status=CorporateActionAuditStatus.PENDING,
                research_eligible=False,
                failed_step="TIMESTAMP_CHECK",
            )

        # 3. DUPLICATE CHECK — caller supplies dedup context (e.g. via ledger/store);
        #    left as a no-op placeholder here since dedup needs a persistence layer.
        #    Do not fabricate dedup logic without the store — flag as OPEN if needed
        #    beyond simple in-memory sets.

        # 4. ZERO-RANGE FLAG (informational — does not exclude by itself)
        zero_range = bar.high == bar.low == bar.open == bar.close

        # 5. TRADING SESSION CHECK
        if not self._calendar.is_valid_slot(bar.timestamp_local):
            return HygieneResult(
                bar_result=BarValidationResult(bar, BarValidationStatus.EXCLUDED, "invalid_session_slot"),
                corporate_action_status=CorporateActionAuditStatus.PENDING,
                research_eligible=False,
                failed_step="TRADING_SESSION_CHECK",
            )

        # 6. TRADING HALT CHECK
        status = self._market_status.status_at(bar.symbol, bar.timestamp_utc)
        if status in (MarketStatus.HALTED, MarketStatus.SUSPENDED):
            return HygieneResult(
                bar_result=BarValidationResult(bar, BarValidationStatus.EXCLUDED, "trading_halt"),
                corporate_action_status=CorporateActionAuditStatus.PENDING,
                research_eligible=False,
                failed_step="TRADING_HALT_CHECK",
            )

        # 7. CORPORATE ACTION AUDIT
        ca_status = self._ca_audit_lookup(bar.symbol, bar.timestamp_utc)
        if ca_status == CorporateActionAuditStatus.PENDING:
            return HygieneResult(
                bar_result=BarValidationResult(bar, BarValidationStatus.VALID, "zero_range" if zero_range else None),
                corporate_action_status=ca_status,
                research_eligible=False,
                failed_step="CORPORATE_ACTION_AUDIT",
            )

        # 8. WARM-UP ELIGIBILITY
        ready = self._warmup_check(bar.symbol, bar.timeframe, bar.timestamp_utc)
        if not ready:
            return HygieneResult(
                bar_result=BarValidationResult(bar, BarValidationStatus.VALID, "zero_range" if zero_range else None),
                corporate_action_status=ca_status,
                research_eligible=False,
                failed_step="WARM_UP_ELIGIBILITY",
            )

        return HygieneResult(
            bar_result=BarValidationResult(bar, BarValidationStatus.VALID, "zero_range" if zero_range else None),
            corporate_action_status=ca_status,
            research_eligible=True,
            failed_step=None,
        )


def detect_gap(
    symbol: str,
    timeframe: str,
    previous_bar_ts: datetime,
    current_bar_ts: datetime,
) -> GapAnomalyRecord | None:
    """§13 gap detection. A gap is never a bar — only an anomaly record.

    Does NOT assume gap == trading halt. That requires explicit
    confirmation from a MarketStatusProvider (see confirm_gap below).
    """
    if timeframe not in TIMEFRAME_MINUTES:
        raise ValueError(f"Unknown timeframe for gap detection: {timeframe}")

    threshold = timedelta(minutes=GAP_THRESHOLD_MULTIPLIER * TIMEFRAME_MINUTES[timeframe])
    delta = current_bar_ts - previous_bar_ts
    if delta <= threshold:
        return None

    return GapAnomalyRecord(
        symbol=symbol,
        timeframe=timeframe,
        gap_start=previous_bar_ts,
        gap_end=current_bar_ts,
        status=DataGapStatus.SUSPECTED_GAP,
        detected_at=datetime.utcnow(),
        confirmed_by=None,
    )


def confirm_gap(
    gap: GapAnomalyRecord, market_status_provider: MarketStatusProvider
) -> GapAnomalyRecord:
    """Upgrade SUSPECTED_GAP -> CONFIRMED_HALT only on explicit evidence.
    Without confirmation, SUSPECTED_GAP must remain as-is (§13)."""
    status = market_status_provider.status_at(gap.symbol, gap.gap_start)
    if status in (MarketStatus.HALTED, MarketStatus.SUSPENDED):
        return GapAnomalyRecord(
            symbol=gap.symbol,
            timeframe=gap.timeframe,
            gap_start=gap.gap_start,
            gap_end=gap.gap_end,
            status=DataGapStatus.CONFIRMED_HALT,
            detected_at=gap.detected_at,
            confirmed_by=market_status_provider.__class__.__name__,
        )
    return gap
