# Technical Note

## 1. Fixed-income analytics

The fixed-income module implements zero-coupon and coupon-bond valuation under annual or periodic compounding. It calculates Macaulay duration, modified duration, convexity, and DV01/PV01.

The deterministic stress engine reprices instruments exactly under user-defined changes in yield and compares exact P&L against duration-convexity approximation.

## 2. Monte Carlo risk engine

The Monte Carlo module simulates short-rate paths using a Vasicek process. The final simulated rate is used as a simplified yield shift for portfolio repricing. The resulting distribution of portfolio values produces VaR and Expected Shortfall estimates.

This is intentionally simple and transparent. It is not a full term-structure model.

## 3. RAG stress assistant

The retrieval module chunks local markdown documents and applies TF-IDF vectorisation with cosine similarity. Retrieved snippets are used to structure a scenario template.

The system is retrieval-augmented but not externally generative. This makes it safe to deploy without API keys and avoids unsupported LLM claims.

## 4. ABM market stress simulator

The ABM module uses heterogeneous trading behaviours and a simplified market impact function. Agent selling pressure affects price, volatility affects spread, and drawdowns can create forced selling.

The purpose is to demonstrate feedback-loop logic, not to estimate a production-level market microstructure model.
