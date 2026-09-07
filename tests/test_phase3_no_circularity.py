import pytest
from datetime import datetime
from tekb_core.research import ResearchLedger, check_research_eligibility
from tekb_core.constants import RESEARCH_WARMUP_BARS, MIN_RESEARCH_BARS
def test_hypothesis_must_have_batch():
    ledger = ResearchLedger()
    h = ledger.register_hypothesis("H1", "Test momentum", "BATCH_001")
    assert h.batch_id == "BATCH_001"
def test_freeze_prevents_new_hypothesis():
    ledger = ResearchLedger()
    ledger.register_batch("BATCH_X")
    ledger.register_hypothesis("H1", "desc", "BATCH_X")
    ledger.freeze_batch("BATCH_X", datetime(2024, 1, 1))
    with pytest.raises(ValueError, match="already frozen"):
        ledger.register_hypothesis("H2", "late hypothesis", "BATCH_X")
def test_no_future_leak():
    ledger = ResearchLedger()
    ledger.register_hypothesis("H1", "desc", "BATCH_F")
    cutoff = datetime(2024, 6, 15)
    ledger.freeze_batch("BATCH_F", cutoff)
    assert ledger.validate_no_future_leak("H1", datetime(2024, 6, 14)) is True
    assert ledger.validate_no_future_leak("H1", datetime(2024, 6, 16)) is False
def test_research_eligibility_warmup():
    assert check_research_eligibility(RESEARCH_WARMUP_BARS + MIN_RESEARCH_BARS) is True
    assert check_research_eligibility(RESEARCH_WARMUP_BARS + MIN_RESEARCH_BARS - 1) is False
def test_batch_requires_freeze_for_validation():
    ledger = ResearchLedger()
    ledger.register_hypothesis("H1", "desc", "BATCH_NF")
    with pytest.raises(ValueError, match="not frozen"):
        ledger.validate_no_future_leak("H1", datetime.utcnow())