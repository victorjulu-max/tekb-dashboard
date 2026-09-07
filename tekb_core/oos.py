"""
TEKB Core v1.4 - Phase 4 OOS + Snapshot Lock
IS/OOS strict split - anti future leak
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Tuple, Literal
from.constants import DEFAULT_IS_START, DEFAULT_IS_END, DEFAULT_OOS_START

def _parse_date(d) -> date:
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return datetime.strptime(d, "%Y-%m-%d").date()
    raise TypeError(f"Invalid date type: {d}")

@dataclass(frozen=True)
class OOSConfig:
    is_start: date
    is_end: date
    oos_start: date
    oos_end: date # WAJIB explicit, tidak boleh default "today"

    def __post_init__(self):
        # OOS_END must be explicit
        if self.oos_end is None:
            raise ValueError("OOS_END must be explicit absolute date, not None or today (V1.4 §36)")
        if not (self.is_start <= self.is_end < self.oos_start <= self.oos_end):
            raise ValueError(
                f"Invalid IS/OOS order: must be IS_START <= IS_END < OOS_START <= OOS_END, "
                f"got {self.is_start} <= {self.is_end} < {self.oos_start} <= {self.oos_end}"
            )

    @classmethod
    def from_defaults(cls, oos_end: str | date | datetime) -> "OOSConfig":
        if not oos_end:
            raise ValueError("OOS_END must be explicit (no default)")
        return cls(
            is_start=_parse_date(DEFAULT_IS_START),
            is_end=_parse_date(DEFAULT_IS_END),
            oos_start=_parse_date(DEFAULT_OOS_START),
            oos_end=_parse_date(oos_end),
        )

    def classify(self, d: str | date | datetime) -> Literal["IS", "OOS", "OUT_OF_RANGE"]:
        dd = _parse_date(d)
        if self.is_start <= dd <= self.is_end:
            return "IS"
        if self.oos_start <= dd <= self.oos_end:
            return "OOS"
        return "OUT_OF_RANGE"

    def validate_no_leak(self, hypothesis_locked_date: str | date | datetime) -> bool:
        """Hypothesis harus di-lock sebelum OOS_START"""
        locked = _parse_date(hypothesis_locked_date)
        return locked < self.oos_start

def split_is_oos(dates: List[str | date | datetime], config: OOSConfig) -> Tuple[List[date], List[date]]:
    is_dates = []
    oos_dates = []
    for d in dates:
        dd = _parse_date(d)
        cls = config.classify(dd)
        if cls == "IS":
            is_dates.append(dd)
        elif cls == "OOS":
            oos_dates.append(dd)
    return is_dates, oos_dates

def check_oos_freshness(oos_data_date: str | date | datetime, config: OOSConfig) -> bool:
    """Pastikan OOS data tidak dipakai saat IS research"""
    dd = _parse_date(oos_data_date)
    return config.oos_start <= dd <= config.oos_end