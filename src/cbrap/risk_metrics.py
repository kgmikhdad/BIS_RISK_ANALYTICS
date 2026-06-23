from __future__ import annotations

import numpy as np
import pandas as pd


def value_at_risk(losses: np.ndarray | pd.Series, confidence: float = 0.99) -> float:
    """Historical/simulation VaR for a loss distribution."""
    arr = np.asarray(losses, dtype=float)
    if arr.size == 0:
        raise ValueError("losses cannot be empty")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    return float(np.quantile(arr, confidence))


def expected_shortfall(losses: np.ndarray | pd.Series, confidence: float = 0.99) -> float:
    arr = np.asarray(losses, dtype=float)
    var = value_at_risk(arr, confidence)
    tail = arr[arr >= var]
    if tail.size == 0:
        return var
    return float(np.mean(tail))


def max_drawdown(values: np.ndarray | pd.Series) -> float:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError("values cannot be empty")
    running_max = np.maximum.accumulate(arr)
    drawdown = arr / running_max - 1.0
    return float(np.min(drawdown))


def risk_summary(losses: np.ndarray | pd.Series, confidence: float = 0.99) -> dict[str, float]:
    arr = np.asarray(losses, dtype=float)
    return {
        "mean_loss": float(np.mean(arr)),
        "median_loss": float(np.median(arr)),
        "volatility_loss": float(np.std(arr, ddof=1)),
        "probability_positive_loss": float(np.mean(arr > 0)),
        "var": value_at_risk(arr, confidence),
        "expected_shortfall": expected_shortfall(arr, confidence),
    }
