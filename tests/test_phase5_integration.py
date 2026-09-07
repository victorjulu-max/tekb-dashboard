from datetime import datetime
from tekb_core.pipeline import TEKBPipeline
from tekb_core.oos import OOSConfig
from tekb_core.research import ResearchLedger

def test_integration_research_oos_combined():
    # full V1.4 flow: hygiene -> OOS lock -> research -> no leak
    oos = OOSConfig.from_defaults(oos_end="2024-12-31")
    pipe = TEKBPipeline(oos_end="2024-12-31")
    pipe.run_hygiene(200)
    pipe.build_adjusted_view()
    pipe.check_market_status()
    pipe.check_calendar()
    pipe.check_research_eligibility()
    assert pipe.state.research_eligible
    # batch locked before OOS
    cutoff = datetime(2022,12,31)
    res = pipe.run_research([0.001,0.02,0.8], "BATCH_FINAL", ["H_FINAL_1","H_FINAL_2","H_FINAL_3"], cutoff)
    assert res["n_rejected"] >= 1
    # validate OOS classification still correct after research
    assert oos.classify("2021-01-01") == "IS"
    assert oos.classify("2024-01-01") == "OOS"

def test_integration_ledger_oos_independence():
    ledger = ResearchLedger()
    ledger.register_hypothesis("H_INT", "Integration test", "BATCH_INT")
    ledger.freeze_batch("BATCH_INT", datetime(2022,12,31))
    # future leak check
    assert ledger.validate_no_future_leak("H_INT", datetime(2022,12,30)) is True
    assert ledger.validate_no_future_leak("H_INT", datetime(2023,1,2)) is False