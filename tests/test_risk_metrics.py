import numpy as np

from src.cbrap.risk_metrics import expected_shortfall, max_drawdown, value_at_risk


def test_var_and_es_ordering():
    losses = np.array([0, 1, 2, 3, 10], dtype=float)
    var = value_at_risk(losses, 0.8)
    es = expected_shortfall(losses, 0.8)
    assert es >= var


def test_max_drawdown_negative():
    values = np.array([100, 110, 90, 95], dtype=float)
    dd = max_drawdown(values)
    assert dd < 0
