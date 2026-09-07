from tekb_core.validation import validate_constants, validate_oos_constants, validate_full_v14, validate_pipeline_state
from tekb_core.pipeline import TEKBPipeline

def test_validate_constants():
    c = validate_constants()
    assert all(c.values()), f"Failed: {c}"

def test_validate_oos_constants():
    o = validate_oos_constants()
    assert all(o.values())

def test_validate_full_v14():
    full = validate_full_v14()
    assert full["v14_compliant"] is True
    assert full["golden_ready"] is True
    assert full["pipeline_version"] == "v0.2"
    assert full["build_spec_version"] == "v1.4"

def test_validate_pipeline_state_ok():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(100)
    pipe.build_adjusted_view()
    pipe.check_market_status()
    pipe.check_calendar()
    pipe.check_research_eligibility()
    errors = validate_pipeline_state(pipe.state)
    assert errors == []

def test_validate_pipeline_state_not_ok():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(10) # insufficient
    errors = validate_pipeline_state(pipe.state)
    assert len(errors) >= 1