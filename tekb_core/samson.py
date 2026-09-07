"""
SAMSON Engine — §10 (same-slot baseline), §15 (warm-up), §16 (detection),
§17 (declustering), §38 (anti-look-ahead).

This module implements the DETECTION mechanics only. It does not decide
final providers, calendar, or corporate-action formulas (those are OPEN
items — see providers.py). It must not be modified to change the
methodology itself (threshold, baseline method, etc.) — those live in
constants.py precisely so a change is visible as a parameter_version bump,
not a silent code edit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from .constants import (
    DECLUSTER_GAP_CANDLES,
    MIN_REQUIRED,
    ROLLING_WINDOW,
    SAMSON_THRESHOLD,
)
from .models import SamsonDirection, WarmupStatus


@dataclass(frozen=True)
class SlotIdentity:
    """§10 — minimal slot identity. NORMAL_DAY vs special day must never mix."""
    session_date: str  # YYYY-MM-DD
    session_id: str    # "I" or "II"
    slot_id: str        # e.g. "10:00"
    slot_start: str
    slot_end: str
    day_type: str        # NORMAL_DAY / HOLIDAY / HALF_DAY_RAMADAN / SPECIAL_HALF_DAY


@dataclass(frozen=True)
class SlotObservation:
    """One historical observation of volume for a given same-slot identity,
    used to build the baseline. `bar_index` must be a monotonically
    increasing index within (symbol, timeframe) so declustering distance
    is well-defined."""
    slot: SlotIdentity
    bar_index: int
    timestamp_utc: datetime
    volume: float


def warmup_status(same_slot_history: Sequence[SlotObservation]) -> WarmupStatus:
    """§15 — SAMSON must never be computed unless status is READY."""
    n = len(same_slot_history)
    if n < MIN_REQUIRED:
        return WarmupStatus.WARMUP if n > 0 else WarmupStatus.INSUFFICIENT_BASELINE
    return WarmupStatus.READY


def same_slot_baseline(same_slot_history: Sequence[SlotObservation]) -> float:
    """§10 — baseline volume for a slot = rolling mean over the same slot
    identity, using only observations strictly BEFORE the bar being
    evaluated (caller is responsible for not including the current bar
    or any future bar — see anti-look-ahead note below)."""
    if not same_slot_history:
        raise ValueError("Cannot compute baseline with no same-slot history")
    window = same_slot_history[-ROLLING_WINDOW:]
    return sum(obs.volume for obs in window) / len(window)


def detect_samson(
    current_volume: float,
    current_close: float,
    current_open: float,
    baseline_volume: float,
    warmup: WarmupStatus,
) -> tuple[bool, float, SamsonDirection | None]:
    """§16 — SAMSON = volume / same-slot baseline >= threshold.

    ANTI-LOOK-AHEAD (§38): this function must only ever be called with
    `baseline_volume` computed from bars strictly before the current bar's
    timestamp `t`. It must never be called with information from t+1,
    t+3, t+5, or t+10 — those horizons are for evaluating forward returns
    AFTER an event has already been determined, never for detecting it.

    Returns (is_samson, relative_volume, direction). Direction is None
    when is_samson is False.
    """
    if warmup != WarmupStatus.READY:
        # SAMSON must never be created outside of READY (§15).
        return False, 0.0, None

    if baseline_volume <= 0:
        raise ValueError("baseline_volume must be positive")

    rv = current_volume / baseline_volume
    if rv < SAMSON_THRESHOLD:
        return False, rv, None

    direction = (
        SamsonDirection.SAMSON_PLUS
        if current_close >= current_open
        else SamsonDirection.SAMSON_MINUS
    )
    return True, rv, direction


@dataclass(frozen=True)
class DeclusterCandidate:
    event_id: str
    symbol: str
    timeframe: str
    bar_index: int


def decluster(events: Sequence[DeclusterCandidate]) -> dict[str, tuple[bool, str]]:
    """§17 — basic declustering within (symbol, timeframe) scope.

    No direction filter: SAMSON+ and SAMSON- adjacent events can share a
    cluster. Events must be pre-sorted by bar_index within their
    (symbol, timeframe) group before calling this function.

    Returns {event_id: (is_independent, cluster_id)}.
    """
    result: dict[str, tuple[bool, str]] = {}
    groups: dict[tuple[str, str], list[DeclusterCandidate]] = {}
    for ev in events:
        groups.setdefault((ev.symbol, ev.timeframe), []).append(ev)

    for key, group in groups.items():
        group = sorted(group, key=lambda e: e.bar_index)
        cluster_seq = 0
        cluster_id = f"{key[0]}_{key[1]}_cluster_{cluster_seq}"
        last_index: int | None = None
        for ev in group:
            if last_index is None:
                is_independent = True
            else:
                distance = ev.bar_index - last_index
                is_independent = distance > DECLUSTER_GAP_CANDLES
                if is_independent:
                    cluster_seq += 1
                    cluster_id = f"{key[0]}_{key[1]}_cluster_{cluster_seq}"
            result[ev.event_id] = (is_independent, cluster_id)
            last_index = ev.bar_index

    return result
