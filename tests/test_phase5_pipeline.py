from datetime import datetime
from tekb_core.pipeline import TEKBPipeline

def test_pipeline_full_flow():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(n_bars=100)
    assert pipe.state.hygiene_passed is True
    pipe.build_adjusted_view()
    assert pipe.state.adjusted_view_built is True
    pipe.check_market_status()
    pipe.check_calendar()
    pipe.check_research_eligibility()
    assert pipe.state.research_eligible is True
    result = pipe.run_research(
        p_values=[0.01,0.02,0.3,0.6],
        batch_id="BATCH_GOLDEN_001",
        hypothesis_ids=["H1","H2","H3","H4"],
        cutoff_date=datetime(2022,12,31)
    )
    assert result["n_rejected"] >= 1
    assert result["batch_id"] == "BATCH_GOLDEN_001"

def test_pipeline_compliance_report():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(100)
    pipe.build_adjusted_view()
    pipe.check_market_status()
    pipe.check_calendar()
    report = pipe.get_compliance_report()
    assert report["v14_golden"] is True
    assert report["oos_locked"] is True
    assert report["hygiene_order_locked"] is True

def test_pipeline_no_leak():
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(100)
    pipe.build_adjusted_view()
    pipe.check_market_status()
    pipe.check_calendar()
    pipe.check_research_eligibility()
    pipe.run_research([0.01,0.5], "BATCH_LEAK", ["H_LEAK"], datetime(2022,12,31))
    # data before cutoff + before OOS start = OK
    assert pipe.validate_oos_no_leak("H_LEAK", datetime(2022,12,15)) is True
    # data after OOS start = leak even if before cutoff? should be False because OOS
    assert pipe.validate_oos_no_leak("H_LEAK", datetime(2023,6,1)) is False
