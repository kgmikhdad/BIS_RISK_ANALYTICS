from __future__ import annotations

import numpy as np
import pandas as pd

from .portfolio import portfolio_value
from .risk_metrics import risk_summary


def simulate_vasicek_rates(
    r0: float,
    kappa: float,
    theta: float,
    sigma: float,
    horizon_years: float,
    steps: int,
    n_sims: int,
    seed: int = 42,
) -> np.ndarray:
    """Simulate Vasicek short-rate paths using Euler discretisation."""
    if steps <= 0 or n_sims <= 0:
        raise ValueError("steps and n_sims must be positive")
    rng = np.random.default_rng(seed)
    dt = horizon_years / steps
    rates = np.empty((n_sims, steps + 1), dtype=float)
    rates[:, 0] = r0
    for t in range(1, steps + 1):
        shock = rng.normal(0.0, 1.0, size=n_sims)
        rates[:, t] = rates[:, t - 1] + kappa * (theta - rates[:, t - 1]) * dt + sigma * np.sqrt(dt) * shock
        rates[:, t] = np.maximum(rates[:, t], -0.005)
    return rates


def monte_carlo_portfolio_distribution(
    portfolio_df: pd.DataFrame,
    r0: float = 0.04,
    kappa: float = 0.8,
    theta: float = 0.045,
    sigma: float = 0.015,
    horizon_years: float = 1.0,
    steps: int = 12,
    n_sims: int = 5000,
    confidence: float = 0.99,
    seed: int = 42,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Simulate portfolio values using terminal short-rate shifts.

    The terminal rate shock is applied as a parallel yield shift relative to r0.
    This is a transparent prototype approximation, not a full curve model.
    """
    from .portfolio import reprice_portfolio

    base_value = portfolio_value(portfolio_df)
    paths = simulate_vasicek_rates(r0, kappa, theta, sigma, horizon_years, steps, n_sims, seed)
    terminal_rates = paths[:, -1]
    delta_y = terminal_rates - r0

    values = np.empty(n_sims, dtype=float)
    for i, dy in enumerate(delta_y):
        pnl_table = reprice_portfolio(portfolio_df, float(dy))
        values[i] = base_value + pnl_table["exact_pnl"].sum()

    losses = base_value - values
    sims = pd.DataFrame({"terminal_rate": terminal_rates, "yield_shift": delta_y, "portfolio_value": values, "loss": losses})
    summary = risk_summary(losses, confidence)
    summary["base_portfolio_value"] = base_value
    summary["confidence"] = confidence
    summary["n_sims"] = n_sims
    return sims, summary
