
"""
Provider interfaces Phase 2 OPEN #1 + #2 + #3 — V1.4 FINAL / CODING-FROZEN

OPEN #1 OHLCV: Yahoo MVP + Broker slot (RAW preserve, NORMALIZED dual)
OPEN #2 CorporateAction: CSV manual + Yahoo MVP + Broker/KSEI slot + Composite
OPEN #3 MarketStatus: CSV manual + Manual + Broker/BEI slot + Composite — crucial for SUSPECTED_GAP vs CONFIRMED_HALT separation (V1.4 §13-14)

V1.4 compliance:
- Provider MUST NOT do validation/dedup
- Gap is anomaly, never bar
- HALT confirmation requires explicit MarketStatusProvider evidence
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from .models import CalendarDay, CorporateAction, MarketStatus, RawBar, NormalizedBar, ActionType, DataGapStatus, GapAnomalyRecord
from .constants import LOCAL_TIMEZONE

def raw_to_normalized(raw: RawBar) -> NormalizedBar:
    ts = raw.provider_timestamp
    if ts.tzinfo is None:
        if "yahoo" in raw.source.lower():
            ts_utc = ts.replace(tzinfo=timezone.utc)
        else:
            ts_utc = ts.replace(tzinfo=ZoneInfo(LOCAL_TIMEZONE)).astimezone(timezone.utc)
    else:
        ts_utc = ts.astimezone(timezone.utc)
    ts_local = ts_utc.astimezone(ZoneInfo(LOCAL_TIMEZONE))
    return NormalizedBar(raw.symbol, raw.timeframe, ts_utc, ts_local, raw.open, raw.high, raw.low, raw.close, raw.volume, raw.source)

class OHLCVProvider(ABC):
    @abstractmethod
    def fetch_range(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawBar]: ...
    @abstractmethod
    def latest_available_timestamp(self, symbol: str, timeframe: str) -> Optional[datetime]: ...
    @property
    @abstractmethod
    def source_name(self) -> str: ...

class CorporateActionProvider(ABC):
    @abstractmethod
    def fetch_actions(self, symbol: str, start: datetime, end: datetime) -> list[CorporateAction]: ...
    @property
    def source_name(self) -> str:
        return self.__class__.__name__

class MarketStatusProvider(ABC):
    """
    §14 — V1.4 OPEN #3
    Used ONLY to confirm SUSPECTED_GAP -> CONFIRMED_HALT.
    Must NOT be used to fabricate bars. Returns MarketStatus.
    """
    @abstractmethod
    def status_at(self, symbol: str, timestamp: datetime) -> MarketStatus: ...
    @property
    def source_name(self) -> str:
        return self.__class__.__name__

class TradingCalendarProvider(ABC):
    @abstractmethod
    def is_trading_day(self, date: datetime) -> bool: ...
    @abstractmethod
    def session_slots(self, date: datetime) -> list[CalendarDay]: ...
    @abstractmethod
    def is_valid_slot(self, timestamp: datetime) -> bool: ...

# ---------------- OHLCV ----------------
class CSVProvider(OHLCVProvider):
    def __init__(self, csv_path: str, source_label: str = "csv_import"):
        self._csv_path=csv_path; self._source_label=source_label
    @property
    def source_name(self) -> str: return self._source_label
    def fetch_range(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawBar]:
        bars=[]; fetched_at=datetime.now(timezone.utc)
        with open(self._csv_path, newline="", encoding="utf-8") as f:
            reader=csv.DictReader(f)
            for row in reader:
                if row["symbol"]!=symbol or row["timeframe"]!=timeframe: continue
                ts=datetime.fromisoformat(row["provider_timestamp"])
                if not (start<=ts<=end): continue
                bars.append(RawBar(row["symbol"], row["timeframe"], ts, float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]), float(row["volume"]), row.get("source", self._source_label), dict(row), fetched_at))
        return bars
    def latest_available_timestamp(self, symbol: str, timeframe: str) -> Optional[datetime]:
        all_bars=self.fetch_range(symbol, timeframe, datetime.min.replace(tzinfo=timezone.utc), datetime.max.replace(tzinfo=timezone.utc))
        return max((b.provider_timestamp for b in all_bars), default=None)

class ManualImportProvider(OHLCVProvider):
    def __init__(self, bars: list[RawBar], source_label: str = "manual_import"):
        self._bars=list(bars); self._source_label=source_label
    @property
    def source_name(self) -> str: return self._source_label
    def fetch_range(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawBar]:
        return [b for b in self._bars if b.symbol==symbol and b.timeframe==timeframe and start<=b.provider_timestamp<=end]
    def latest_available_timestamp(self, symbol: str, timeframe: str) -> Optional[datetime]:
        m=[b for b in self._bars if b.symbol==symbol and b.timeframe==timeframe]
        return max((b.provider_timestamp for b in m), default=None)

class YahooProvider(OHLCVProvider):
    def __init__(self, auto_adjust: bool = False): self._auto_adjust=auto_adjust
    @property
    def source_name(self) -> str: return "yahoo"
    def _map_tf(self, tf: str) -> str: return {"1D":"1d","1H":"1h","15M":"15m","5M":"5m","4H":"1h"}.get(tf,"1d")
    def fetch_range(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawBar]:
        try:
            import yfinance as yf
        except ImportError:
            return []
        ysym=symbol if "." in symbol else f"{symbol}.JK"
        interval=self._map_tf(timeframe)
        try:
            df=yf.Ticker(ysym).history(start=start, end=end, interval=interval, auto_adjust=self._auto_adjust, actions=False)
        except Exception:
            return []
        bars=[]; fetched_at=datetime.now(timezone.utc)
        if df.empty: return bars
        for idx,row in df.iterrows():
            pts=idx.to_pydatetime() if hasattr(idx,"to_pydatetime") else idx
            if pts.tzinfo is None: pts=pts.replace(tzinfo=timezone.utc)
            bars.append(RawBar(symbol, timeframe, pts, float(row["Open"]), float(row["High"]), float(row["Low"]), float(row["Close"]), float(row["Volume"]), self.source_name, {"yahoo_symbol":ysym,"interval":interval}, fetched_at))
        return bars
    def latest_available_timestamp(self, symbol: str, timeframe: str) -> Optional[datetime]:
        from datetime import timedelta
        end=datetime.now(timezone.utc); start=end-timedelta(days=5)
        bars=self.fetch_range(symbol,timeframe,start,end)
        return max((b.provider_timestamp for b in bars), default=None)

class BrokerProvider(OHLCVProvider):
    def __init__(self, api_key: Optional[str]=None, source_label: str="broker_stockbit"):
        self._api_key=api_key; self._source_label=source_label
    @property
    def source_name(self) -> str: return self._source_label
    def fetch_range(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> list[RawBar]:
        raise NotImplementedError(f"{self.source_name}.fetch_range() not implemented — provide broker API. YahooProvider remains MVP.")
    def latest_available_timestamp(self, symbol: str, timeframe: str) -> Optional[datetime]:
        raise NotImplementedError(f"{self.source_name}.latest_available_timestamp() not implemented")

# ---------------- Corporate Action ----------------
class CSVCorporateActionProvider(CorporateActionProvider):
    def __init__(self, csv_path: str, source_label: str = "csv_corporate_action"):
        self._csv_path=csv_path; self._source_label=source_label
    @property
    def source_name(self) -> str: return self._source_label
    def fetch_actions(self, symbol: str, start: datetime, end: datetime) -> list[CorporateAction]:
        actions=[]
        with open(self._csv_path, newline="", encoding="utf-8") as f:
            reader=csv.DictReader(f)
            for row in reader:
                if row["symbol"]!=symbol: continue
                ex=datetime.fromisoformat(row["ex_date"])
                if ex.tzinfo is None: ex=ex.replace(tzinfo=timezone.utc)
                if not (start<=ex<=end): continue
                at=ActionType[row["action_type"]]
                ratio=float(row["ratio"]) if row.get("ratio") else None
                cash=float(row["cash_value"]) if row.get("cash_value") else None
                sub_price=float(row["subscription_price"]) if row.get("subscription_price") else None
                ca=CorporateAction(row["action_id"], row["symbol"], at, ex, ratio, cash, row.get("source", self._source_label), datetime.now(timezone.utc))
                if sub_price is not None: ca.__dict__["subscription_price"]=sub_price
                actions.append(ca)
        return sorted(actions, key=lambda a: a.ex_date)

class ManualCorporateActionProvider(CorporateActionProvider):
    def __init__(self, actions: list[CorporateAction], source_label: str="manual_corporate_action"):
        self._actions=list(actions); self._source_label=source_label
    @property
    def source_name(self) -> str: return self._source_label
    def fetch_actions(self, symbol: str, start: datetime, end: datetime) -> list[CorporateAction]:
        return sorted([a for a in self._actions if a.symbol==symbol and start<=a.ex_date<=end], key=lambda a: a.ex_date)

class YahooCorporateActionProvider(CorporateActionProvider):
    @property
    def source_name(self) -> str: return "yahoo_corporate_action"
    def fetch_actions(self, symbol: str, start: datetime, end: datetime) -> list[CorporateAction]:
        try:
            import yfinance as yf
        except ImportError:
            return []
        ysym=symbol if "." in symbol else f"{symbol}.JK"
        try:
            ticker=yf.Ticker(ysym)
            splits=ticker.splits; dividends=ticker.dividends
        except Exception:
            return []
        actions=[]
        if splits is not None and not splits.empty:
            for idx,ratio in splits.items():
                dt=idx.to_pydatetime() if hasattr(idx,"to_pydatetime") else idx
                if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
                if not (start<=dt<=end): continue
                actions.append(CorporateAction(f"{symbol}_SPLIT_{idx.date()}", symbol, ActionType.SPLIT, dt, float(ratio), None, self.source_name, datetime.now(timezone.utc)))
        if dividends is not None and not dividends.empty:
            for idx,cash in dividends.items():
                dt=idx.to_pydatetime() if hasattr(idx,"to_pydatetime") else idx
                if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
                if not (start<=dt<=end): continue
                actions.append(CorporateAction(f"{symbol}_DIV_{idx.date()}", symbol, ActionType.DIVIDEND, dt, None, float(cash), self.source_name, datetime.now(timezone.utc)))
        return sorted(actions, key=lambda a: a.ex_date)

class BrokerCorporateActionProvider(CorporateActionProvider):
    def __init__(self, api_key: Optional[str]=None, source_label: str="broker_ksei"):
        self._api_key=api_key; self._source_label=source_label
    @property
    def source_name(self) -> str: return self._source_label
    def fetch_actions(self, symbol: str, start: datetime, end: datetime) -> list[CorporateAction]:
        raise NotImplementedError(f"{self.source_name}.fetch_actions() not implemented — provide KSEI/broker API. CSV fallback remains MVP.")

class CompositeCorporateActionProvider(CorporateActionProvider):
    def __init__(self, providers: list[CorporateActionProvider]):
        self._providers=providers
    @property
    def source_name(self) -> str: return "composite_" + "+".join(p.source_name for p in self._providers)
    def fetch_actions(self, symbol: str, start: datetime, end: datetime) -> list[CorporateAction]:
        seen=set(); merged=[]
        for p in self._providers:
            try:
                acts=p.fetch_actions(symbol,start,end)
            except NotImplementedError:
                continue
            for a in acts:
                key=(a.action_type, a.ex_date.date(), a.ratio, a.cash_value)
                if key in seen: continue
                seen.add(key); merged.append(a)
        return sorted(merged, key=lambda a: a.ex_date)

# ---------------- Market Status OPEN #3 ----------------

class CSVMarketStatusProvider(MarketStatusProvider):
    """
    V1.4 OPEN #3 — CSV manual fallback for market halt/suspend.
    Expected columns: symbol, timestamp, status, source, confirmed_by
    status values: NORMAL, HALTED, SUSPENDED, RESUMED, SPECIAL_SESSION
    This is the source of truth for CONFIRMED_HALT — not inferred from gap alone.
    """
    def __init__(self, csv_path: str, source_label: str = "csv_market_status"):
        self._csv_path=csv_path; self._source_label=source_label
        self._records: list[dict] = []
        self._load()

    def _load(self):
        try:
            with open(self._csv_path, newline="", encoding="utf-8") as f:
                reader=csv.DictReader(f)
                for row in reader:
                    ts=datetime.fromisoformat(row["timestamp"])
                    if ts.tzinfo is None: ts=ts.replace(tzinfo=timezone.utc)
                    status=MarketStatus[row["status"]]
                    self._records.append({"symbol":row["symbol"], "timestamp":ts, "status":status, "source":row.get("source", self._source_label), "confirmed_by":row.get("confirmed_by")})
        except FileNotFoundError:
            self._records=[]

    @property
    def source_name(self) -> str: return self._source_label

    def status_at(self, symbol: str, timestamp: datetime) -> MarketStatus:
        # Find latest status <= timestamp for symbol
        if timestamp.tzinfo is None:
            timestamp=timestamp.replace(tzinfo=timezone.utc)
        relevant=[r for r in self._records if r["symbol"]==symbol and r["timestamp"]<=timestamp]
        if not relevant:
            return MarketStatus.NORMAL
        latest=max(relevant, key=lambda r: r["timestamp"])
        return latest["status"]

class ManualMarketStatusProvider(MarketStatusProvider):
    """
    In-memory manual provider for tests and audited manual workflows.
    Accepts list of (symbol, timestamp, MarketStatus).
    """
    def __init__(self, statuses: list[tuple[str, datetime, MarketStatus]], source_label: str="manual_market_status"):
        self._statuses=[]
        for sym, ts, st in statuses:
            if ts.tzinfo is None: ts=ts.replace(tzinfo=timezone.utc)
            self._statuses.append((sym, ts, st))
        self._source_label=source_label

    @property
    def source_name(self) -> str: return self._source_label

    def status_at(self, symbol: str, timestamp: datetime) -> MarketStatus:
        if timestamp.tzinfo is None:
            timestamp=timestamp.replace(tzinfo=timezone.utc)
        relevant=[(s,ts,st) for s,ts,st in self._statuses if s==symbol and ts<=timestamp]
        if not relevant:
            return MarketStatus.NORMAL
        latest=max(relevant, key=lambda x: x[1])
        return latest[2]

class BrokerMarketStatusProvider(MarketStatusProvider):
    """
    Slot for final BEI/vendor market status API (trading halt, suspend, special session).
    Must return explicit evidence for CONFIRMED_HALT — never infer from gap alone.
    """
    def __init__(self, api_key: Optional[str]=None, source_label: str="broker_bei"):
        self._api_key=api_key; self._source_label=source_label

    @property
    def source_name(self) -> str: return self._source_label

    def status_at(self, symbol: str, timestamp: datetime) -> MarketStatus:
        raise NotImplementedError(f"{self.source_name}.status_at() not implemented — provide BEI/vendor API. CSV manual fallback remains MVP per V1.4 §14.")

class CompositeMarketStatusProvider(MarketStatusProvider):
    """
    Composite market status — merges multiple sources.
    Precedence: broker_bei > csv > manual (official source wins).
    """
    def __init__(self, providers: list[MarketStatusProvider]):
        self._providers=providers

    @property
    def source_name(self) -> str: return "composite_" + "+".join(p.source_name for p in self._providers)

    def status_at(self, symbol: str, timestamp: datetime) -> MarketStatus:
        # First non-NORMAL status wins (HALTED/SUSPENDED take precedence)
        # If all NORMAL, return NORMAL
        last_normal=MarketStatus.NORMAL
        for p in self._providers:
            try:
                st=p.status_at(symbol, timestamp)
            except NotImplementedError:
                continue
            if st in (MarketStatus.HALTED, MarketStatus.SUSPENDED, MarketStatus.SPECIAL_SESSION):
                return st
            if st==MarketStatus.RESUMED:
                return st
            last_normal=st
        return last_normal

# Helper for gap confirmation workflow (V1.4 §13-14)
def confirm_gap_with_provider(gap: GapAnomalyRecord, provider: MarketStatusProvider) -> GapAnomalyRecord:
    """
    Upgrade SUSPECTED_GAP -> CONFIRMED_HALT only on explicit provider evidence.
    Without confirmation, SUSPECTED_GAP remains as-is per V1.4 §13.
    This prevents misinterpreting IDX holidays as price anomalies.
    """
    from dataclasses import replace
    status=provider.status_at(gap.symbol, gap.gap_start)
    if status in (MarketStatus.HALTED, MarketStatus.SUSPENDED):
        return GapAnomalyRecord(
            symbol=gap.symbol,
            timeframe=gap.timeframe,
            gap_start=gap.gap_start,
            gap_end=gap.gap_end,
            status=DataGapStatus.CONFIRMED_HALT,
            detected_at=gap.detected_at,
            confirmed_by=provider.source_name,
        )
    return gap
