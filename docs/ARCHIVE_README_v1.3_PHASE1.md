# tekb_core — Phase 1: Foundation

Shared research engine package for **TEKB Stock Analyzer**. This is the
single implementation of SAMSON detection logic used by both the laptop
research app and the Vercel operational dashboard — see
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for why this matters.

## Status

This is a **skeleton**, not a finished implementation. It exists to lock
down structure, interfaces, and locked-order rules from *Technical Build
Specification v1.3* before wiring in real data.

Deliberately **not yet implemented** (depends on OPEN items — see §49 of
the spec, and `providers.py`):

- Final OHLCV research provider (OPEN 1)
- Corporate action provider (OPEN 2)
- Market status provider (OPEN 3)
- IDX trading calendar (OPEN 4)
- Corporate action adjustment formulas (§7.1 — split/dividend/rights/bonus)
- Exact dependency version pins (OPEN 5)

Do not fill these in by guessing. Each is a methodological decision that
belongs one layer up (TEKB Definition / Pipeline Specification v0.2), not
a Phase 1 coding decision.

## Install

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Test

```bash
pytest
```

## Package layout

| File | Spec section | Purpose |
|---|---|---|
| `models.py` | §1, §2, §4.1, §6, §9, §12, §16, §24, §27-30, §32 | Shared dataclasses + status enums |
| `providers.py` | §4, §6, §9, §14 | Provider ABCs + MVP CSV/manual providers |
| `hygiene.py` | §11, §12, §13, §14 | LOCKED 8-step check order, gap vs bar |
| `samson.py` | §10, §15, §16, §17, §38 | Same-slot baseline, warm-up gate, detection, decluster |
| `ledger.py` | §24-26, §39 | Append-only SQLite Research Ledger |
| `snapshot.py` | §27 | Reproducible dataset snapshot + content hash |
| `specification.py` | §28-29 | `specification_id` + `fingerprint_hash` |
| `constants.py` | §10-17, §32, §35-36, §43 | Locked default parameters |

## Non-negotiable rules

See §50 of Technical Build Specification v1.3. In particular:

- No look-ahead: SAMSON detection at `t` must never use `t+1..t+10`.
- RAW is immutable; corrections go through `SUPERSEDED`, never overwrite.
- A data gap is an anomaly record, never a synthetic bar.
- `constants.py` values are locked — changing them changes
  `parameter_version` / `fingerprint_hash`, not just "tuning a number".

## Deployment architecture

GitHub (this repo) → Laptop (research engine) + Vercel (operational
dashboard), both importing this same `tekb_core` package. Full rationale
in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
