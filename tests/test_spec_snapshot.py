
from tekb_core.specification import build_specification_version, compute_fingerprint_hash
from tekb_core.snapshot import build_dataset_snapshot, compute_content_hash
from datetime import datetime

def test_specification_id_vs_hash_split():
    spec = build_specification_version("v1","cal1","ca1","det1","param1")
    assert spec.specification_id != spec.fingerprint_hash
    assert len(spec.fingerprint_hash) == 64  # SHA256 hex

def test_fingerprint_deterministic():
    h1 = compute_fingerprint_hash("v1","cal1","ca1","det1","param1")
    h2 = compute_fingerprint_hash("v1","cal1","ca1","det1","param1")
    assert h1 == h2

def test_snapshot_has_v14_fields():
    ch = compute_content_hash(["row1","row2"])
    snap = build_dataset_snapshot("DS-20240101-001","ohlcv1","ca1","cal1","csv","BBCA","1D", datetime(2024,1,1), datetime(2024,1,31), 2, ch)
    assert hasattr(snap, "universe")
    assert hasattr(snap, "timeframe")
    assert hasattr(snap, "start_date")
    assert hasattr(snap, "end_date")
    assert hasattr(snap, "row_count")
    assert hasattr(snap, "content_hash")
    assert snap.row_count == 2

def test_content_hash_sorted():
    h1 = compute_content_hash(["b","a"])
    h2 = compute_content_hash(["a","b"])
    assert h1 == h2
