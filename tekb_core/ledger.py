"""
Research Ledger — §24 (append-only), §25 (entry status), §26 (corporate
action correction), §39 (immutability rules).

Hard rules enforced here:
  - No UPDATE of an existing event row's core fields.
  - No DELETE, ever.
  - Corrections happen via `supersede_event`, which inserts a NEW row and
    flips the OLD row's entry_status to SUPERSEDED — it never rewrites the
    old row's result fields.
"""

from __future__ import annotations

import sqlite3
from dataclasses import asdict
from datetime import datetime
from typing import Optional

from .models import EntryStatus, ResearchLedgerEntry, SamsonEvent

_SCHEMA = """
CREATE TABLE IF NOT EXISTS ledger_entries (
    event_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    direction TEXT NOT NULL,
    volume REAL NOT NULL,
    baseline_volume REAL NOT NULL,
    rv REAL NOT NULL,
    price REAL NOT NULL,
    research_eligible INTEGER NOT NULL,
    corporate_action_status TEXT NOT NULL,
    is_independent INTEGER NOT NULL,
    cluster_id TEXT NOT NULL,
    dataset_snapshot_id TEXT NOT NULL,
    specification_id TEXT NOT NULL,
    exclusion_reason TEXT,
    entry_status TEXT NOT NULL,
    supersedes_event_id TEXT,
    superseded_by_event_id TEXT,
    correction_reason TEXT,
    correction_timestamp TEXT,
    cost_model_id TEXT NOT NULL,
    multiple_testing_family_id TEXT,
    created_at TEXT NOT NULL
);
"""


class ResearchLedger:
    """Append-only SQLite-backed ledger. One instance per database file."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def insert_entry(self, entry: ResearchLedgerEntry) -> None:
        """Insert a brand-new ledger row. Raises if event_id already exists —
        this is intentional; corrections must go through supersede_entry."""
        ev = entry.event
        self._conn.execute(
            """
            INSERT INTO ledger_entries (
                event_id, symbol, timeframe, timestamp_utc, direction,
                volume, baseline_volume, rv, price, research_eligible,
                corporate_action_status, is_independent, cluster_id,
                dataset_snapshot_id, specification_id, exclusion_reason,
                entry_status, supersedes_event_id, superseded_by_event_id,
                correction_reason, correction_timestamp, cost_model_id,
                multiple_testing_family_id, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ev.event_id,
                ev.symbol,
                ev.timeframe,
                ev.timestamp_utc.isoformat(),
                ev.direction.value,
                ev.volume,
                ev.baseline_volume,
                ev.rv,
                ev.price,
                int(ev.research_eligible),
                ev.corporate_action_status.value,
                int(ev.is_independent),
                ev.cluster_id,
                ev.dataset_snapshot_id,
                ev.specification_id,
                entry.exclusion_reason,
                entry.entry_status.value,
                entry.supersedes_event_id,
                entry.superseded_by_event_id,
                entry.correction_reason,
                entry.correction_timestamp.isoformat() if entry.correction_timestamp else None,
                entry.cost_model_id,
                entry.multiple_testing_family_id,
                entry.created_at.isoformat(),
            ),
        )
        self._conn.commit()

    def supersede_entry(
        self,
        old_event_id: str,
        new_entry: ResearchLedgerEntry,
        correction_reason: str,
    ) -> None:
        """§26 — correction workflow. Never UPDATEs old result fields;
        only flips entry_status/superseded_by_event_id on the old row and
        inserts the new row with supersedes_event_id set."""
        now = datetime.utcnow().isoformat()
        cur = self._conn.execute(
            "SELECT entry_status FROM ledger_entries WHERE event_id = ?",
            (old_event_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Cannot supersede unknown event_id: {old_event_id}")

        self._conn.execute(
            """
            UPDATE ledger_entries
            SET entry_status = ?, superseded_by_event_id = ?,
                correction_reason = ?, correction_timestamp = ?
            WHERE event_id = ?
            """,
            (
                EntryStatus.SUPERSEDED.value,
                new_entry.event.event_id,
                correction_reason,
                now,
                old_event_id,
            ),
        )
        self._conn.commit()
        self.insert_entry(new_entry)

    def query_active(self, symbol: Optional[str] = None) -> list[sqlite3.Row]:
        """Default statistics view: ACTIVE ONLY (§26)."""
        self._conn.row_factory = sqlite3.Row
        if symbol:
            cur = self._conn.execute(
                "SELECT * FROM ledger_entries WHERE entry_status = ? AND symbol = ?",
                (EntryStatus.ACTIVE.value, symbol),
            )
        else:
            cur = self._conn.execute(
                "SELECT * FROM ledger_entries WHERE entry_status = ?",
                (EntryStatus.ACTIVE.value,),
            )
        return cur.fetchall()

    def query_all_including_superseded(self) -> list[sqlite3.Row]:
        """Explicit opt-in to see superseded rows (never the default)."""
        self._conn.row_factory = sqlite3.Row
        cur = self._conn.execute("SELECT * FROM ledger_entries")
        return cur.fetchall()
