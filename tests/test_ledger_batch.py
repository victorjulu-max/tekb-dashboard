
from tekb_core.models import ResearchBatch, ResearchBatchStatus, ResearchHypothesis, HypothesisStatus
from datetime import datetime

def test_research_batch_exists():
    batch = ResearchBatch("batch1", (), ResearchBatchStatus.OPEN)
    assert batch.research_batch_id == "batch1"

def test_hypothesis_requires_batch_id():
    # should fail if missing research_batch_id
    try:
        # This should require research_batch_id per V1.4
        h = ResearchHypothesis(hypothesis_id="h1", b0_definition="b0", b1_definition="b1", oos_start=datetime(2023,1,1), oos_end=datetime(2024,1,1), locked_at=None, universe=(), status=HypothesisStatus.DRAFT)
        assert False, "Should require research_batch_id"
    except TypeError:
        assert True

def test_hypothesis_with_batch():
    h = ResearchHypothesis(research_batch_id="batch1", hypothesis_id="h1", b0_definition="b0", b1_definition="b1", oos_start=datetime(2023,1,1), oos_end=datetime(2024,1,1), locked_at=None, universe=(), status=HypothesisStatus.DRAFT)
    assert h.research_batch_id == "batch1"

def test_constants_v14():
    from tekb_core.constants import BUILD_SPEC_VERSION
    assert BUILD_SPEC_VERSION == "v1.4"
