from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

BondType = Literal["zero_coupon", "coupon"]


@dataclass(frozen=True)
class BondAnalytics:
    price: float
    macaulay_duration: float
    modified_duration: float
    convexity: float
    dv01: float


def _validate_inputs(face_value: float, ytm: float, maturity_years: float, frequency: int) -> None:
    if face_value <= 0:
        raise ValueError("face_value must be positive")
    if ytm <= -0.99:
        raise ValueError("yield_to_maturity is unrealistically low")
    if maturity_years <= 0:
        raise ValueError("maturity_years must be positive")
    if frequency <= 0:
        raise ValueError("frequency must be a positive integer")


def cash_flows(
    face_value: float,
    coupon_rate: float,
    maturity_years: float,
    frequency: int = 1,
    instrument_type: BondType = "coupon",
) -> pd.DataFrame:
    """Return a cash-flow table for a zero-coupon or coupon bond.

    The time grid is rounded to the nearest full coupon period. This is appropriate
    for a compact prototype but should be replaced by exact day-count conventions
    in a production valuation engine.
    """
    _validate_inputs(face_value, 0.0, maturity_years, frequency)
    periods = max(1, int(round(maturity_years * frequency)))
    times = np.arange(1, periods + 1) / frequency

    if instrument_type == "zero_coupon" or coupon_rate == 0:
        cfs = np.zeros(periods)
        cfs[-1] = face_value
    else:
        coupon = face_value * coupon_rate / frequency
        cfs = np.full(periods, coupon)
        cfs[-1] += face_value

    return pd.DataFrame({"period": np.arange(1, periods + 1), "time_years": times, "cash_flow": cfs})


def bond_price(
    face_value: float,
    coupon_rate: float,
    ytm: float,
    maturity_years: float,
    frequency: int = 1,
    instrument_type: BondType = "coupon",
) -> float:
    """Price a fixed-rate bond using periodic compounding."""
    _validate_inputs(face_value, ytm, maturity_years, frequency)
    cf = cash_flows(face_value, coupon_rate, maturity_years, frequency, instrument_type)
    discount = (1 + ytm / frequency) ** cf["period"].to_numpy()
    return float(np.sum(cf["cash_flow"].to_numpy() / discount))


def analytics(
    face_value: float,
    coupon_rate: float,
    ytm: float,
    maturity_years: float,
    frequency: int = 1,
    instrument_type: BondType = "coupon",
) -> BondAnalytics:
    """Calculate price, duration, modified duration, convexity, and DV01."""
    _validate_inputs(face_value, ytm, maturity_years, frequency)
    cf = cash_flows(face_value, coupon_rate, maturity_years, frequency, instrument_type)
    periods = cf["period"].to_numpy(dtype=float)
    times = cf["time_years"].to_numpy(dtype=float)
    flows = cf["cash_flow"].to_numpy(dtype=float)
    discount = (1 + ytm / frequency) ** periods
    pv = flows / discount
    price = float(np.sum(pv))

    if price <= 0:
        raise ValueError("computed bond price must be positive")

    macaulay = float(np.sum(times * pv) / price)
    modified = float(macaulay / (1 + ytm / frequency))

    convexity_periodic = np.sum(flows * periods * (periods + 1) / (discount * (1 + ytm / frequency) ** 2)) / price
    convexity_years = float(convexity_periodic / (frequency**2))
    dv01 = float(price * modified * 0.0001)

    return BondAnalytics(
        price=price,
        macaulay_duration=macaulay,
        modified_duration=modified,
        convexity=convexity_years,
        dv01=dv01,
    )


def duration_convexity_price_change(price: float, modified_duration: float, convexity: float, delta_y: float) -> float:
    """Approximate price change using duration and convexity.

    ΔP ≈ P[-D_mod Δy + 0.5 C (Δy)^2]
    """
    return float(price * (-modified_duration * delta_y + 0.5 * convexity * delta_y**2))


def price_yield_curve(
    face_value: float,
    coupon_rate: float,
    maturity_years: float,
    frequency: int,
    instrument_type: BondType,
    ytm_min: float = 0.0,
    ytm_max: float = 0.12,
    n: int = 100,
) -> pd.DataFrame:
    yields = np.linspace(ytm_min, ytm_max, n)
    prices = [bond_price(face_value, coupon_rate, y, maturity_years, frequency, instrument_type) for y in yields]
    return pd.DataFrame({"yield": yields, "price": prices})
