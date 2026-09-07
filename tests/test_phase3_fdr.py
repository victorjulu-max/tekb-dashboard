from tekb_core.research import benjamini_hochberg, fdr_control_summary
def test_bh_basic():
    pvals = [0.01, 0.04, 0.03, 0.20, 0.50]
    rejected, qvals = benjamini_hochberg(pvals, alpha=0.05)
    assert len(rejected) == 5
    assert rejected[0] == True
    assert qvals[0] <= 0.05
    assert rejected[4] == False
def test_bh_empty():
    r, q = benjamini_hochberg([], alpha=0.05)
    assert r == [] and q == []
def test_bh_all_significant():
    pvals = [0.001, 0.002, 0.003]
    rejected, _ = benjamini_hochberg(pvals, alpha=0.05)
    assert all(rejected)
def test_bh_none_significant():
    pvals = [0.6, 0.7, 0.8]
    rejected, _ = benjamini_hochberg(pvals, alpha=0.05)
    assert not any(rejected)
def test_fdr_summary_structure():
    pvals = [0.01, 0.02, 0.3]
    summary = fdr_control_summary(pvals, alpha=0.05)
    assert summary["n_tests"] == 3
    assert summary["fdr_controlled"] is True