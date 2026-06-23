# Central-Bank Risk Analytics Prototypes

**A Streamlit-ready technical portfolio for fixed-income risk analytics, retrieval-augmented stress testing, and agent-based market-stress simulation.**

This repository contains three connected prototypes designed for a central-bank-facing Banking / Middle Office analytics environment:

1. **Fixed-Income Risk Analytics Dashboard** — bond pricing, duration, convexity, DV01/PV01, scenario P\&L, Monte Carlo VaR/Expected Shortfall.
2. **Retrieval-Augmented Stress-Testing Assistant** — a transparent local retrieval system that converts public stress-testing notes into structured scenario templates.
3. **Agent-Based Market-Stress Simulator** — a stylised liquidity-stress model in which heterogeneous market participants generate endogenous price impact and risk-limit breaches.

The implementation uses **synthetic and public-style data only**. It does not use, reproduce, or imply access to confidential institutional data, BIS-internal documents, or proprietary systems.

---

## Why this prototype exists

The objective is to demonstrate how a recent graduate with quantitative economics, financial-market modelling, Python implementation, and central-bank research exposure can translate an analytical question into a reproducible working prototype.

The project is intentionally framed as a **research and analytics prototype**, not a production trading/risk system. The focus is on:

- clear financial intuition,
- reproducible Python code,
- interpretable risk metrics,
- transparent model assumptions,
- documented limitations,
- and an interface that can be understood by both technical and non-technical users.

---

## Repository structure

```text
central-bank-risk-analytics-prototypes/
├── app.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── LICENSE
├── .streamlit/
│   └── config.toml
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── data/
│   ├── synthetic_portfolio.csv
│   ├── synthetic_yield_curve.csv
│   └── docs/
│       ├── fixed_income_risk_notes.md
│       ├── stress_testing_notes.md
│       └── model_governance_notes.md
├── docs/
│   ├── deployment_guide.md
│   ├── interview_followup_note.md
│   └── technical_note.md
├── notebooks/
│   └── prototype_walkthrough.ipynb
├── src/
│   └── cbrap/
│       ├── __init__.py
│       ├── fixed_income.py
│       ├── risk_metrics.py
│       ├── monte_carlo.py
│       ├── portfolio.py
│       ├── scenarios.py
│       ├── rag.py
│       ├── abm.py
│       └── utils.py
└── tests/
    ├── test_fixed_income.py
    ├── test_risk_metrics.py
    └── test_abm.py
```

---

## Prototype 1: Fixed-Income Middle Office Risk Analytics Dashboard

### Purpose

This module demonstrates a compact analytics workflow for fixed-income instruments and a synthetic reserve-style portfolio. It is relevant for Middle Office analytics because it connects valuation, sensitivity analysis, risk measurement, and stress testing.

### Core functions

- Zero-coupon bond pricing.
- Coupon bond pricing.
- Yield-price relationship.
- Clean interpretation of time-to-maturity effects.
- Macaulay duration.
- Modified duration.
- Convexity.
- DV01/PV01.
- Portfolio-level market value.
- Scenario P\&L under yield shocks.
- Monte Carlo loss distribution.
- Value-at-Risk and Expected Shortfall.

### Main formulas

For a zero-coupon bond:

```math
P = \frac{F}{(1+y)^T}
```

where:

- `P` = price,
- `F` = face value,
- `y` = annual yield,
- `T` = time to maturity in years.

For a coupon bond:

```math
P = \sum_{t=1}^{N} \frac{C}{(1+y/f)^t} + \frac{F}{(1+y/f)^N}
```

where:

- `C` = coupon payment per period,
- `f` = coupon frequency,
- `N = T × f` = number of coupon periods.

Modified duration:

```math
D_{mod} = \frac{D_{Mac}}{1+y/f}
```

Approximate price change:

```math
\frac{\Delta P}{P} \approx -D_{mod}\Delta y + \frac{1}{2}Convexity(\Delta y)^2
```

DV01/PV01:

```math
DV01 \approx P \times D_{mod} \times 0.0001
```

---

## Prototype 2: Retrieval-Augmented Stress-Testing Assistant

### Purpose

This component is a lightweight **Retrieval-Augmented Generation-style** prototype, implemented without external LLM APIs. It retrieves relevant text from a small public-style document corpus and uses the retrieved context to populate structured stress-scenario templates.

This is deliberately transparent. The retrieval method is simple enough to inspect, explain, and validate.

### What RAG means here

RAG is not model training. It is a two-step workflow:

1. **Retrieve** relevant external text or data from a knowledge base.
2. **Generate or structure** an answer using that retrieved context.

In this repository, the generation step is intentionally rule-based for reproducibility. A more advanced version could connect the retrieved context to a local or enterprise-approved LLM.

### Features

- Markdown document ingestion.
- Text chunking.
- TF-IDF vectorisation.
- Cosine-similarity retrieval.
- Source-cited retrieved passages.
- Scenario template generation.
- Risk-channel mapping.

Example user query:

```text
Design a stress scenario for a sudden upward shift in global interest rates.
```

Example output fields:

- scenario name,
- primary shock,
- affected risk factors,
- transmission channels,
- expected portfolio effect,
- metrics to monitor,
- retrieved supporting passages.

---

## Prototype 3: Agent-Based Market-Stress Simulator

### Purpose

This module demonstrates an agent-based market-liquidity stress simulation. The objective is to show how micro-level behaviour can create aggregate risk amplification.

Unlike a two-player policy game, an ABM contains **heterogeneous interacting agents**. Aggregate outcomes emerge from those interactions.

### Agents

The simulation includes stylised versions of:

- long-only investors,
- liquidity-constrained sellers,
- risk-limit agents,
- market makers,
- external shock process.

### Mechanism

1. A market shock reduces asset value.
2. Some investors sell in response to losses or risk limits.
3. Market makers widen spreads under order imbalance.
4. Price impact increases as aggregate selling rises.
5. Forced selling can amplify the original shock.
6. Portfolio losses and VaR breaches are recorded.

### Outputs

- simulated price path,
- bid-ask spread path,
- aggregate sell pressure,
- portfolio value path,
- risk-limit breach count,
- final drawdown,
- scenario diagnostics.

---

## Streamlit application

The application has four pages:

1. **Overview** — project purpose and architecture.
2. **Fixed-Income Analytics** — instrument-level pricing and risk sensitivity.
3. **Portfolio Stress Testing** — scenario shocks, Monte Carlo VaR and Expected Shortfall.
4. **RAG + ABM Lab** — retrieval-based scenario design and agent-based stress simulation.

Run locally:

```bash
git clone https://github.com/kgmikhdad/BIS_RISK_ANALYTICS.git
cd BIS_RISK_ANALYTICS
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Streamlit Cloud deployment

1. Push this repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Select this repository.
4. Use:

```text
Main file path: app.py
```

5. No secrets or API keys are needed.

A more detailed guide is available in:

```text
docs/deployment_guide.md
```

---

## Installation for development

```bash
git clone https://github.com/kgmikhdad/BIS_RISK_ANALYTICS.git
cd BIS_RISK_ANALYTICS
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
```

---

## Tests

The repository includes unit tests for:

- zero-coupon bond pricing,
- coupon bond pricing,
- duration and convexity behaviour,
- VaR and Expected Shortfall,
- ABM simulation output validity.

Run:

```bash
pytest -q
```

Expected result:

```text
6 passed
```

---

## Design principles

### 1. Financial interpretability

Each output should correspond to a recognisable financial concept: price, yield, duration, convexity, DV01, VaR, Expected Shortfall, drawdown, or liquidity stress.

### 2. Reproducibility

The code avoids hidden data dependencies. Synthetic datasets are included in the repository. Random seeds are exposed where relevant.

### 3. Modularity

Analytics functions are separated from the Streamlit interface. This makes the code easier to test and extend.

### 4. Transparency

The RAG module uses TF-IDF retrieval rather than a black-box hosted LLM. This keeps the demo inspectable and avoids dependency on external APIs.

### 5. Conservative claims

The project does not claim to be a production risk engine. It is a prototype showing analytical implementation capacity.

---

## Possible extensions

### Fixed-income analytics

- Add full yield-curve bootstrapping.
- Add key-rate duration.
- Add multi-currency portfolio valuation.
- Add FX risk and hedging layers.
- Add historical scenario replay.
- Add liquidity-adjusted valuation.

### Risk measurement

- Add GARCH volatility models.
- Add filtered historical simulation.
- Add expected shortfall backtesting.
- Add stress-period calibration.
- Add scenario aggregation across market factors.

### RAG system

- Add PDF ingestion.
- Add document-level metadata.
- Add embedding models.
- Add local LLM support.
- Add source-grounded audit trails.
- Add human approval workflow.

### ABM simulation

- Add heterogeneous balance sheets.
- Add collateral and margin calls.
- Add repo-market funding constraints.
- Add network exposures.
- Add calibration to public market data.
- Add policy/intervention agents.

---

## Limitations

This repository is a prototype. Important limitations include:

- simplified yield-curve dynamics,
- simplified agent behaviour,
- synthetic portfolio data,
- no real trading or reserve-management data,
- no production model governance layer,
- no independently validated risk engine,
- no connection to internal banking systems,
- no claim of regulatory adequacy.

The purpose is to demonstrate technical structure, implementation discipline, and analytical reasoning, not to provide a production-ready tool.

---

## Ethical and confidentiality statement

This repository uses only synthetic data and public-style documentation created for demonstration. It does not contain confidential data, internal institutional information, proprietary pricing models, or restricted documents.

The prototype is intended for educational and interview-portfolio purposes only.

---

## Suggested professional framing

When sharing this repository, use concise wording:

> I built a small supplementary technical portfolio inspired by our discussion around fixed-income analytics, Monte Carlo simulation, AI/RAG systems, and agent-based modelling. The repository uses only synthetic data and is intended as a research/analytics prototype, not a production system. It demonstrates how I would structure a reproducible implementation project from financial intuition to code, testing, documentation, and dashboard presentation.

---

## Author

Muhammed Mikhdad K. G.

Quantitative economics, central banking research, financial-market modelling, machine learning, and computational macro-finance.
