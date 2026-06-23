from src.cbrap.abm import ABMSettings, simulate_market_stress


def test_abm_runs_and_returns_expected_length():
    settings = ABMSettings(n_steps=10, seed=1)
    df, diagnostics = simulate_market_stress(settings)
    assert len(df) == 11
    assert "max_drawdown" in diagnostics
    assert df["price_index"].min() > 0
