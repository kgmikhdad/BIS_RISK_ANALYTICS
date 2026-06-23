from __future__ import annotations

import pandas as pd

from .portfolio import reprice_portfolio


DEFAULT_SCENARIOS = {
    "Mild parallel shock (+50 bps)": 0.005,
    "Severe parallel shock (+200 bps)": 0.020,
    "Interview-style repricing shock (+500 bps)": 0.050,
    "Rate rally (-100 bps)": -0.010,
}


def run_parallel_scenarios(portfolio_df: pd.DataFrame, scenarios: dict[str, float] | None = None) -> pd.DataFrame:
    scenarios = scenarios or DEFAULT_SCENARIOS
    rows = []
    for name, shock in scenarios.items():
        pnl = reprice_portfolio(portfolio_df, shock)
        rows.append(
            {
                "scenario": name,
                "yield_shock_bps": shock * 10000,
                "portfolio_exact_pnl": pnl["exact_pnl"].sum(),
                "duration_convexity_pnl": pnl["duration_convexity_pnl"].sum(),
                "approximation_error": pnl["approximation_error"].sum(),
            }
        )
    return pd.DataFrame(rows)


def classify_scenario_query(query: str) -> dict[str, str]:
    q = query.lower()
    if any(k in q for k in ["liquidity", "spread", "market depth", "forced selling"]):
        return {
            "scenario_family": "Liquidity stress",
            "shock": "Bid-ask spread widening and higher price impact",
            "transmission_channel": "Lower market depth raises exit cost and can amplify mark-to-market losses.",
            "primary_metrics": "Liquidity-adjusted loss, drawdown, VaR/ES, spread proxy",
        }
    if any(k in q for k in ["rate", "yield", "duration", "curve"]):
        return {
            "scenario_family": "Interest-rate stress",
            "shock": "Parallel yield shift, steepener/flattening scenario, or sudden repricing",
            "transmission_channel": "Higher yields reduce fixed-income prices through duration and convexity exposure.",
            "primary_metrics": "PV loss, DV01, duration, convexity, VaR/ES",
        }
    if any(k in q for k in ["fx", "currency", "dollar", "euro"]):
        return {
            "scenario_family": "Foreign-exchange stress",
            "shock": "Currency appreciation/depreciation against portfolio base currency",
            "transmission_channel": "FX translation changes reserve portfolio value and may interact with hedges.",
            "primary_metrics": "FX P&L, hedge ratio, portfolio VaR",
        }
    return {
        "scenario_family": "General market stress",
        "shock": "Joint move in rates, volatility, and liquidity",
        "transmission_channel": "Market repricing affects portfolio valuation and risk limits.",
        "primary_metrics": "P&L, VaR/ES, drawdown, breach indicators",
    }
