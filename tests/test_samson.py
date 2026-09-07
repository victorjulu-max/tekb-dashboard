
from datetime import datetime
from tekb_core.samson import warmup_status, same_slot_baseline, detect_samson, decluster, SlotIdentity, SlotObservation, DeclusterCandidate
from tekb_core.models import WarmupStatus
from tekb_core.constants import MIN_REQUIRED, DECLUSTER_GAP_CANDLES, SAMSON_THRESHOLD

def make_obs(n):
    slot = SlotIdentity("2024-01-02","I","10:00","10:00","10:05","NORMAL_DAY")
    return [SlotObservation(slot, i, datetime(2024,1,2), 1000+i) for i in range(n)]

def test_warmup_insufficient():
    assert warmup_status(make_obs(0)) == WarmupStatus.INSUFFICIENT_BASELINE
    assert warmup_status(make_obs(5)) == WarmupStatus.WARMUP

def test_warmup_ready():
    assert warmup_status(make_obs(MIN_REQUIRED)) == WarmupStatus.READY

def test_baseline_mean():
    obs = make_obs(20)
    b = same_slot_baseline(obs)
    assert b > 0

def test_samson_detection_ready():
    is_s, rv, dir = detect_samson(3000, 106, 100, 1000, WarmupStatus.READY)
    assert is_s
    assert rv == 3.0

def test_samson_not_ready():
    is_s, rv, dir = detect_samson(3000, 106, 100, 1000, WarmupStatus.WARMUP)
    assert not is_s

def test_declustering_le_rule():
    # distance <= gap => non-independent
    evs = [DeclusterCandidate("e1","BBCA","1D",0), DeclusterCandidate("e2","BBCA","1D",DECLUSTER_GAP_CANDLES), DeclusterCandidate("e3","BBCA","1D",DECLUSTER_GAP_CANDLES+1)]
    res = decluster(evs)
    assert res["e1"][0] == True  # independent
    assert res["e2"][0] == False  # distance == gap => NOT independent per V1.4
    assert res["e3"][0] == False  # still within gap from e1? Actually last_index is e2, distance 1 => not independent. This tests <= rule
