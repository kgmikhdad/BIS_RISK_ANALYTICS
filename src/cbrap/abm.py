from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .risk_metrics import max_drawdown


@dataclass(frozen=True)
class ABMSettings:
    n_steps: int = 120
    seed: int = 7
    initial_price: float = 100.0
    initial_portfolio_units: float = 1_000_000
    fundamental_volatility: float = 0.004
    price_impact: float = 0.018
    base_spread: float = 0.0008
    spread_sensitivity: float = 0.035
    forced_sale_threshold: float = -0.035
    forced_sale_intensity: float = 0.45
    liquidity_seller_intensity: float = 0.18
    market_maker_capacity: float = 0.35


def simulate_market_stress(settings: ABMSettings = ABMSettings()) -> tuple[pd.DataFrame, dict[str, float]]:
    rng = np.random.default_rng(settings.seed)
    price = np.empty(settings.n_steps + 1)
    spread = np.empty(settings.n_steps + 1)
    imbalance = np.empty(settings.n_steps + 1)
    forced_selling = np.empty(settings.n_steps + 1)
    portfolio_value = np.empty(settings.n_steps + 1)

    price[0] = settings.initial_price
    spread[0] = settings.base_spread
    imbalance[0] = 0.0
    forced_selling[0] = 0.0
    portfolio_value[0] = price[0] * settings.initial_portfolio_units

    running_peak = portfolio_value[0]

    for t in range(1, settings.n_steps + 1):
        fundamental_return = rng.normal(0.0, settings.fundamental_volatility)
        previous_drawdown = portfolio_value[t - 1] / running_peak - 1.0

        liquidity_seller_order = settings.liquidity_seller_intensity * max(0.0, -fundamental_return) * rng.uniform(0.5, 1.5)
        forced_order = 0.0
        if previous_drawdown < settings.forced_sale_threshold:
            forced_order = settings.forced_sale_intensity * abs(previous_drawdown) * rng.uniform(0.8, 1.4)

        stabilising_market_maker = -settings.market_maker_capacity * (liquidity_seller_order + forced_order)
        net_order = liquidity_seller_order + forced_order + stabilising_market_maker
        price_impact_return = -settings.price_impact * net_order
        total_return = fundamental_return + price_impact_return

        price[t] = max(1.0, price[t - 1] * (1 + total_return))
        imbalance[t] = net_order
        forced_selling[t] = forced_order
        recent_vol = np.std(np.diff(np.log(price[max(0, t - 10) : t + 1]))) if t > 2 else settings.fundamental_volatility
        spread[t] = settings.base_spread + settings.spread_sensitivity * (abs(net_order) + recent_vol)
        portfolio_value[t] = price[t] * settings.initial_portfolio_units
        running_peak = max(running_peak, portfolio_value[t])

    df = pd.DataFrame(
        {
            "step": np.arange(settings.n_steps + 1),
            "price_index": price,
            "spread_proxy": spread,
            "net_order_imbalance": imbalance,
            "forced_selling": forced_selling,
            "portfolio_value": portfolio_value,
        }
    )
    losses = portfolio_value[0] - portfolio_value
    diagnostics = {
        "initial_value": float(portfolio_value[0]),
        "final_value": float(portfolio_value[-1]),
        "total_pnl": float(portfolio_value[-1] - portfolio_value[0]),
        "max_drawdown": max_drawdown(portfolio_value),
        "max_spread_proxy": float(np.max(spread)),
        "forced_selling_events": float(np.sum(forced_selling > 0)),
        "worst_loss": float(np.max(losses)),
    }
    return df, diagnostics
