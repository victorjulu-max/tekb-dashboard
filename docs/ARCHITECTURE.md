# Deployment Architecture — ARCHITECTURE LOCKED / IMPLEMENTATION LAYER

This document is an **implementation-layer** addition to Technical Build
Specification v1.3. It does not modify TEKB Definition or Pipeline
Specification v0.2, and it is not a reason to create v1.4.

## Three components, one system

```text
                 TEKB
                  │
       ┌──────────┴──────────┐
       │                     │
   METHODOLOGY           IMPLEMENTATION
       │                     │
   Pipeline v0.2      Technical Build v1.3
       │                     │
       │          ┌──────────┼──────────┐
       │          │          │          │
       │       GitHub      Laptop    Vercel
```

| Component | Role | Owns |
|---|---|---|
| **GitHub** | Source of truth: code | Source code, `tekb_core`, specs, tests, versions/tags |
| **Laptop** | Source of truth: research data | RAW, NORMALIZED, Adjusted Research View, SQLite, Parquet, full Research Ledger, backtest, OOS, bootstrap, fingerprints |
| **Vercel** | Source of truth: online status | Web dashboard, API, cron daily detection, lightweight cloud DB (daily events/alerts) |

## Single Research Engine principle

The laptop and Vercel must **never** run their own separate SAMSON
implementations. Both import the same `tekb_core` package from this
repository. This is why `tekb_core` exists as an installable package
rather than being duplicated into each app:

```text
GitHub
  └── tekb_core/           ← ONE implementation
         │
    ┌────┴────┐
    ▼         ▼
 LAPTOP    VERCEL
research   daily/live
```

Without this, laptop and Vercel can silently diverge — e.g. laptop
detects "SAMSON = Event A" while Vercel's own copy detects "SAMSON =
Event B" for the same bar. That divergence is exactly what this
architecture exists to prevent.

## What Vercel is allowed to produce

Vercel-side detection results are operational signals only:

```text
DETECTED / WATCH / POTENTIAL_EDGE
```

They are **never** automatically promoted to:

```text
TESTED / OOS_VALIDATED / PROVEN
```

Those statuses can only come from the Research Engine + Research Ledger
on the laptop, following the full Pipeline v0.2 chain (IS/OOS, multiple
testing correction, etc.). A Vercel-detected event is not research
evidence by itself.

## Data flow

**Research mode** (laptop): Provider → RAW → NORMALIZED → DATA HYGIENE →
CORPORATE ACTION → RESEARCH-ELIGIBLE → SAMSON → RESEARCH LEDGER → B0/B1 →
BACKTEST → IS/OOS → ROBUSTNESS → PROVEN / OOS_VALIDATED.

**Operational mode** (Vercel): Provider → Vercel Cron → shared `tekb_core`
detection logic → eligibility check → SAMSON → Daily Event → Cloud DB →
Web Dashboard.

## Storage notes

- Vercel KV is sunset. Use a Vercel Marketplace storage/database service
  (e.g. Redis/Upstash) for the lightweight operational store.
- Vercel does support Python Functions, including longer execution
  durations on Pro/Enterprise — but this is **not** a reason to move the
  research engine off the laptop. The split (laptop = heavy research,
  Vercel = lightweight operational service) is a deliberate simplicity /
  cost / auditability choice, not a technical limitation being worked
  around.

## Why a change in SAMSON parameters is safe under this architecture

Because `tekb_core` lives in one place (GitHub) and both laptop and
Vercel import it, a change like `SAMSON threshold: 2.5 → 3.0` produces a
new `detector_version`/`parameter_version`, which produces a new
`specification_id` and `fingerprint_hash` (see `specification.py`). Old
OOS results are never silently altered — they stay tied to the old
fingerprint. This matches the auditability principle in §28-29 and §37
of the Technical Build Specification.
