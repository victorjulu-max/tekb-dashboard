from tekb_core.research import falsification_test
def test_falsification_real_vs_fake():
    real_p = [0.001, 0.002, 0.01, 0.02, 0.03]
    fake_p = [0.6, 0.7, 0.8, 0.9, 0.5]
    res = falsification_test(real_p, fake_p, alpha=0.05)
    assert res["real_rejected"] >= 2
    assert res["fake_rejected"] == 0
    assert res["passes_falsification"] is True
def test_falsification_both_null():
    real_p = [0.6, 0.7]
    fake_p = [0.6, 0.7]
    res = falsification_test(real_p, fake_p, alpha=0.05)
    assert res["passes_falsification"] is True
