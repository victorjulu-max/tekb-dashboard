from tekb_core.research import permutation_test, generate_null_distribution
def test_permutation_greater():
    null = [0.1, -0.2, 0.05, -0.1, 0.0, 0.15]
    p = permutation_test(0.5, null, alternative="greater")
    assert 0 <= p <= 0.2
def test_permutation_less():
    null = [0.1, -0.2, 0.05]
    p = permutation_test(-1.0, null, alternative="less")
    assert 0 <= p <= 0.3
def test_permutation_two_sided():
    null = [0.1, -0.1, 0.05, -0.05]
    p = permutation_test(1.0, null, alternative="two-sided")
    assert 0 < p <= 1.0
def test_generate_null_distribution():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    null = generate_null_distribution(data, n_permutations=100, seed=123)
    assert len(null) == 100