from __future__ import annotations

import pandas as pd


def as_percent(x: float, digits: int = 2) -> str:
    return f"{100 * x:.{digits}f}%"


def as_bps(x: float, digits: int = 1) -> str:
    return f"{10000 * x:.{digits}f} bps"


def money(x: float, currency: str = "EUR") -> str:
    return f"{currency} {x:,.2f}"


def format_dataframe_numeric(df: pd.DataFrame, digits: int = 4) -> pd.DataFrame:
    out = df.copy()
    for col in out.select_dtypes(include="number").columns:
        out[col] = out[col].round(digits)
    return out
