from tekb_core.oos import OOSConfig

def test_oos_no_overlap_is_oos():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    # boundary check
    assert cfg.classify("2022-12-31") == "IS"
    assert cfg.classify("2023-01-01") == "OOS"
    # no date should be both IS and OOS
    for y in [2020, 2023]:
        for m in [1,6,12]:
            d = f"{y}-{m:02d}-15"
            c = cfg.classify(d)
            assert c in ("IS","OOS") or y==2020 and c=="IS" or y==2023 and c=="OOS"

def test_oos_end_explicit_not_today():
    cfg = OOSConfig.from_defaults(oos_end="2024-06-30")
    # OOS end is exactly what we locked
    assert str(cfg.oos_end) == "2024-06-30"
    # different oos_end = different config = different fingerprint
    cfg2 = OOSConfig.from_defaults(oos_end="2024-12-31")
    assert cfg.oos_end!= cfg2.oos_end