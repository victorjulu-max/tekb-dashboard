from tekb_core.oos import OOSConfig
from tekb_core.snapshot import validate_snapshot_oos_lock

def test_snapshot_oos_lock_validation():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    snapshot = {"oos_end": "2024-12-31", "metadata": {}}
    report = validate_snapshot_oos_lock(snapshot, cfg)
    assert report["is_locked"] is True
    assert report["v14_compliant"] is True
    assert report["snapshot_oos_match"] is True

def test_snapshot_oos_mismatch():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    snapshot = {"oos_end": "2023-12-31"}
    report = validate_snapshot_oos_lock(snapshot, cfg)
    assert report["snapshot_oos_match"] is False
    assert report["is_locked"] is True # config itself still locked

def test_snapshot_without_oos_field_still_locked():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    snapshot = {}
    report = validate_snapshot_oos_lock(snapshot, cfg)
    assert report["is_locked"] is True