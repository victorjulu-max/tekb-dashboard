from tekb_core.constants import PIPELINE_VERSION, BUILD_SPEC_VERSION, HYGIENE_CHECK_ORDER
from tekb_core.pipeline import TEKBPipeline
from tekb_core.validation import validate_full_v14

def test_golden_tag_requirements():
    # requirements for v1.4-FINAL-GOLDEN
    assert PIPELINE_VERSION == "v0.2"
    assert BUILD_SPEC_VERSION == "v1.4"
    assert len(HYGIENE_CHECK_ORDER) == 8
    assert HYGIENE_CHECK_ORDER[0] == "SCHEMA_CHECK"
    assert HYGIENE_CHECK_ORDER[-1] == "WARM_UP_ELIGIBILITY"

def test_golden_pipeline_100_bars():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(100)
    pipe.build_adjusted_view()
    pipe.check_market_status()
    pipe.check_calendar()
    pipe.check_research_eligibility()
    report = pipe.get_compliance_report()
    assert report["v14_golden"] is True
    assert report["oos_end"] == "2024-12-31"

def test_golden_full_compliance():
    full = validate_full_v14()
    assert full["golden_ready"] is True
    assert full["v14_compliant"] is True