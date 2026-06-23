from __future__ import annotations

from pathlib import Path

import pandas as pd

from .fixed_income import analytics, bond_price, duration_convexity_price_change


REQUIRED_COLUMNS = {
    "instrument_id",
    "instrument_type",
    "face_value",
    "coupon_rate",
    "yield_to_maturity",
    "maturity_years",
    "frequency",
    "quantity",
}


def load_portfolio(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Portfolio file missing columns: {sorted(missing)}")
    return df


def enrich_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        a = analytics(
            face_value=float(row["face_value"]),
            coupon_rate=float(row["coupon_rate"]),
            ytm=float(row["yield_to_maturity"]),
            maturity_years=float(row["maturity_years"]),
            frequency=int(row["frequency"]),
            instrument_type=row["instrument_type"],
        )
        position_value = a.price * float(row["quantity"])
        rows.append(
            {
                **row.to_dict(),
                "price": a.price,
                "position_value": position_value,
                "macaulay_duration": a.macaulay_duration,
                "modified_duration": a.modified_duration,
                "convexity": a.convexity,
                "dv01_per_100_face": a.dv01,
                "position_dv01": a.dv01 * float(row["quantity"]),
            }
        )
    enriched = pd.DataFrame(rows)
    total_value = enriched["position_value"].sum()
    enriched["portfolio_weight"] = enriched["position_value"] / total_value if total_value else 0
    return enriched


def portfolio_value(df: pd.DataFrame) -> float:
    return float(enrich_portfolio(df)["position_value"].sum())


def reprice_portfolio(df: pd.DataFrame, delta_y: float) -> pd.DataFrame:
    """Apply a uniform yield shift and return exact and approximate P&L by instrument."""
    base = enrich_portfolio(df)
    rows = []
    for _, row in base.iterrows():
        new_y = float(row["yield_to_maturity"]) + delta_y
        new_price = bond_price(
            face_value=float(row["face_value"]),
            coupon_rate=float(row["coupon_rate"]),
            ytm=new_y,
            maturity_years=float(row["maturity_years"]),
            frequency=int(row["frequency"]),
            instrument_type=row["instrument_type"],
        )
        exact_pnl = (new_price - float(row["price"])) * float(row["quantity"])
        approx_per_bond = duration_convexity_price_change(
            float(row["price"]), float(row["modified_duration"]), float(row["convexity"]), delta_y
        )
        approx_pnl = approx_per_bond * float(row["quantity"])
        rows.append(
            {
                "instrument_id": row["instrument_id"],
                "base_yield": row["yield_to_maturity"],
                "shocked_yield": new_y,
                "base_price": row["price"],
                "shocked_price": new_price,
                "exact_pnl": exact_pnl,
                "duration_convexity_pnl": approx_pnl,
                "approximation_error": exact_pnl - approx_pnl,
            }
        )
    return pd.DataFrame(rows)
