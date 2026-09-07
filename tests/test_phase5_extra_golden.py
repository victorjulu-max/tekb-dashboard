from tekb_core.pipeline import TEKBPipeline
from tekb_core.validation import validate_full_v14
from tekb_core.oos import OOSConfig
from datetime import datetime

def test_extra_golden_1_oos_end_explicit_golden():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    assert cfg.oos_end is not None

def test_extra_golden_2_pipeline_version():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    assert pipe.state.version == "v0.2"

def test_extra_golden_3_build_spec():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    assert pipe.state.build_spec == "v1.4"

def test_extra_golden_4_hygiene_order():
    from tekb_core.constants import HYGIENE_CHECK_ORDER
    assert len(HYGIENE_CHECK_ORDER) == 8

def test_extra_golden_5_full_v14_golden():
    full = validate_full_v14()
    assert full["golden_ready"] is True

def test_extra_golden_6_research_batch_freeze():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(100)
    pipe.build_adjusted_view()
    pipe.check_market_status()
    pipe.check_calendar()
    pipe.check_research_eligibility()
    r = pipe.run_research([0.01,0.9], "BATCH_EXTRA", ["H_EXTRA"], datetime(2022,12,31))
    assert r["batch_id"] == "BATCH_EXTRA"

def test_extra_golden_7_compliance_report_golden():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(100)
    pipe.build_adjusted_view()
    pipe.check_market_status()
    pipe.check_calendar()
    report = pipe.get_compliance_report()
    assert report["v14_golden"] is True
    assert report["oos_end"] == "2024-12-31"