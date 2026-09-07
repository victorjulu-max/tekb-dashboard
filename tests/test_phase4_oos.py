import pytest
from datetime import date
from tekb_core.oos import OOSConfig, split_is_oos, check_oos_freshness

def test_oos_config_defaults():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    assert str(cfg.is_start) == "2016-01-01"
    assert str(cfg.is_end) == "2022-12-31"
    assert str(cfg.oos_start) == "2023-01-01"
    assert str(cfg.oos_end) == "2024-12-31"

def test_oos_config_requires_explicit_end():
    with pytest.raises(ValueError, match="OOS_END must be explicit"):
        OOSConfig.from_defaults(oos_end=None)
    with pytest.raises(ValueError, match="OOS_END must be explicit"):
        OOSConfig.from_defaults(oos_end="")

def test_oos_config_order_validation():
    with pytest.raises(ValueError, match="Invalid IS/OOS order"):
        OOSConfig(
            is_start=date(2023,1,1),
            is_end=date(2022,12,31),
            oos_start=date(2023,1,1),
            oos_end=date(2024,12,31)
        )

def test_classify_is_oos():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    assert cfg.classify("2020-06-15") == "IS"
    assert cfg.classify("2023-06-15") == "OOS"
    assert cfg.classify("2015-01-01") == "OUT_OF_RANGE"
    assert cfg.classify("2025-01-01") == "OUT_OF_RANGE"

def test_split_is_oos():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    dates = ["2020-01-01", "2021-06-01", "2023-02-01", "2024-01-01", "2015-01-01"]
    is_dates, oos_dates = split_is_oos(dates, cfg)
    assert len(is_dates) == 2
    assert len(oos_dates) == 2

def test_validate_no_leak():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    assert cfg.validate_no_leak("2022-12-15") is True # locked before OOS
    assert cfg.validate_no_leak("2023-01-02") is False # locked after OOS start = leak

def test_oos_freshness():
    cfg = OOSConfig.from_defaults(oos_end="2024-12-31")
    assert check_oos_freshness("2023-06-01", cfg) is True
    assert check_oos_freshness("2022-06-01", cfg) is False
