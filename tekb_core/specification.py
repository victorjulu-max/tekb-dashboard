"""
Specification version + fingerprint (§28-29).

Per the spec: the cryptographic fingerprint must NOT be used directly as
database identity. `specification_id` is the database identifier;
`fingerprint_hash` is the immutable fingerprint derived from it.

If ANY of the six version components change, this must produce a NEW
specification_id and a NEW fingerprint_hash. Old events are not
automatically superseded just because the specification changed —
that decision belongs to the correction workflow in ledger.py, not here.
"""

from __future__ import annotations

import hashlib
import json
import uuid

from .constants import BUILD_SPEC_VERSION, PIPELINE_VERSION
from .models import SpecificationVersion


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def compute_fingerprint_hash(
    data_version: str,
    calendar_version: str,
    corporate_action_version: str,
    detector_version: str,
    parameter_version: str,
    pipeline_version: str = PIPELINE_VERSION,
) -> str:
    canonical_specification = {
        "data_version": data_version,
        "calendar_version": calendar_version,
        "corporate_action_version": corporate_action_version,
        "pipeline_version": pipeline_version,
        "detector_version": detector_version,
        "parameter_version": parameter_version,
    }
    return hashlib.sha256(
        _canonical_json(canonical_specification).encode("utf-8")
    ).hexdigest()


def build_specification_version(
    data_version: str,
    calendar_version: str,
    corporate_action_version: str,
    detector_version: str,
    parameter_version: str,
    pipeline_version: str = PIPELINE_VERSION,
    specification_id: str | None = None,
) -> SpecificationVersion:
    """Builds a SpecificationVersion. `specification_id` defaults to a
    fresh UUID4 if not supplied by the caller's persistence layer (e.g.
    an existing row lookup keyed by fingerprint_hash should be checked
    by the caller first, so identical specs reuse the same
    specification_id instead of minting a new one every time)."""
    fingerprint_hash = compute_fingerprint_hash(
        data_version=data_version,
        calendar_version=calendar_version,
        corporate_action_version=corporate_action_version,
        detector_version=detector_version,
        parameter_version=parameter_version,
        pipeline_version=pipeline_version,
    )
    return SpecificationVersion(
        specification_id=specification_id or str(uuid.uuid4()),
        fingerprint_hash=fingerprint_hash,
        data_version=data_version,
        calendar_version=calendar_version,
        corporate_action_version=corporate_action_version,
        pipeline_version=pipeline_version,
        detector_version=detector_version,
        parameter_version=parameter_version,
    )


# Convenience: the build-spec version this tekb_core package implements.
# Not a substitute for detector_version/parameter_version, which track
# the actual SAMSON code + constants.py values.
IMPLEMENTS_BUILD_SPEC = BUILD_SPEC_VERSION
