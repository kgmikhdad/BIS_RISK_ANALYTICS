from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.cbrap.abm import ABMSettings, simulate_market_stress
from src.cbrap.fixed_income import analytics, price_yield_curve
from src.cbrap.monte_carlo import monte_carlo_portfolio_distribution, simulate_vasicek_rates
from src.cbrap.portfolio import enrich_portfolio, load_portfolio, reprice_portfolio
from src.cbrap.rag import generate_scenario_card, retrieve
from src.cbrap.scenarios import run_parallel_scenarios
from src.cbrap.utils import format_dataframe_numeric, money

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DOCS_DIR = DATA_DIR / "docs"
PORTFOLIO_PATH = DATA_DIR / "synthetic_portfolio.csv"

st.set_page_config(
    page_title="Central-Bank Risk Analytics Prototypes",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def get_portfolio() -> pd.DataFrame:
    return load_portfolio(PORTFOLIO_PATH)


st.sidebar.title("Prototype Navigation")
page = st.sidebar.radio(
    "Choose module",
    [
        "Overview",
        "Fixed-Income Analytics",
        "Monte Carlo VaR / ES",
        "RAG Stress Assistant",
        "Agent-Based Stress Simulation",
        "Governance and Limitations",
    ],
)

portfolio = get_portfolio()

if page == "Overview":
    st.title("Central-Bank Risk Analytics Prototypes")
    st.markdown(
        """
        This Streamlit app demonstrates three connected implementation prototypes for a central-bank-facing Banking / Middle Office analytics context:

        1. **Fixed-income risk analytics**: pricing, duration, convexity, DV01/PV01, and scenario P&L.
        2. **Monte Carlo risk simulation**: interest-rate-path simulation, VaR, and Expected Shortfall.
        3. **RAG + ABM extensions**: retrieval-augmented stress-scenario design and agent-based liquidity stress simulation.

        All data are synthetic. The app is designed as a transparent research/analytics prototype, not a production risk engine.
        """
    )

    enriched = enrich_portfolio(portfolio)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio market value", money(enriched["position_value"].sum()))
    c2.metric("Total DV01", money(enriched["position_dv01"].sum()))
    c3.metric("No. instruments", f"{len(enriched)}")
    c4.metric("Weighted duration", f"{(enriched['portfolio_weight'] * enriched['modified_duration']).sum():.2f}")

    st.subheader("Synthetic portfolio")
    st.dataframe(format_dataframe_numeric(enriched), use_container_width=True)

    fig = px.bar(enriched, x="instrument_id", y="position_value", title="Position market value by instrument")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Fixed-Income Analytics":
    st.title("Fixed-Income Analytics Dashboard")
    st.markdown("Price/yield relationship, duration, convexity, DV01, and deterministic stress P&L.")

    st.subheader("Single-instrument price-yield demonstration")
    col1, col2, col3 = st.columns(3)
    with col1:
        face_value = st.number_input("Face value", min_value=1.0, value=100.0, step=10.0)
        coupon_rate = st.slider("Coupon rate", 0.0, 0.10, 0.00, 0.005)
    with col2:
        ytm = st.slider("Yield to maturity", 0.0, 0.15, 0.05, 0.0025)
        maturity = st.slider("Maturity in years", 0.25, 30.0, 1.0, 0.25)
    with col3:
        frequency = st.selectbox("Coupon frequency", [1, 2, 4], index=0)
        instrument_type = "zero_coupon" if coupon_rate == 0 else "coupon"

    a = analytics(face_value, coupon_rate, ytm, maturity, frequency, instrument_type)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Price", f"{a.price:.4f}")
    k2.metric("Modified duration", f"{a.modified_duration:.4f}")
    k3.metric("Convexity", f"{a.convexity:.4f}")
    k4.metric("DV01", f"{a.dv01:.6f}")

    curve = price_yield_curve(face_value, coupon_rate, maturity, frequency, instrument_type, 0, 0.15, 120)
    fig = px.line(curve, x="yield", y="price", title="Price-yield relationship")
    fig.add_vline(x=ytm, line_dash="dash")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Portfolio deterministic stress scenarios")
    shock_bps = st.slider("Custom parallel yield shock", -300, 600, 200, 25)
    repriced = reprice_portfolio(portfolio, shock_bps / 10000)
    scen = run_parallel_scenarios(portfolio)
    custom_row = pd.DataFrame(
        [
            {
                "scenario": f"Custom shock ({shock_bps:+.0f} bps)",
                "yield_shock_bps": shock_bps,
                "portfolio_exact_pnl": repriced["exact_pnl"].sum(),
                "duration_convexity_pnl": repriced["duration_convexity_pnl"].sum(),
                "approximation_error": repriced["approximation_error"].sum(),
            }
        ]
    )
    scen = pd.concat([scen, custom_row], ignore_index=True)
    st.dataframe(format_dataframe_numeric(scen, 2), use_container_width=True)

    fig = px.bar(scen, x="scenario", y="portfolio_exact_pnl", title="Portfolio exact P&L under yield shocks")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Monte Carlo VaR / ES":
    st.title("Monte Carlo VaR and Expected Shortfall")
    st.markdown("Simulates short-rate paths using a Vasicek process and reprices the portfolio under terminal rate shocks.")

    col1, col2, col3 = st.columns(3)
    with col1:
        r0 = st.slider("Initial rate", 0.0, 0.10, 0.04, 0.0025)
        theta = st.slider("Long-run mean", 0.0, 0.10, 0.045, 0.0025)
    with col2:
        kappa = st.slider("Mean reversion speed", 0.05, 3.0, 0.8, 0.05)
        sigma = st.slider("Rate volatility", 0.001, 0.05, 0.015, 0.001)
    with col3:
        horizon = st.slider("Horizon years", 0.25, 3.0, 1.0, 0.25)
        n_sims = st.slider("Number of simulations", 500, 10000, 3000, 500)
        confidence = st.selectbox("Confidence", [0.95, 0.975, 0.99], index=2)

    sims, summary = monte_carlo_portfolio_distribution(
        portfolio,
        r0=r0,
        kappa=kappa,
        theta=theta,
        sigma=sigma,
        horizon_years=horizon,
        steps=max(4, int(12 * horizon)),
        n_sims=n_sims,
        confidence=confidence,
        seed=42,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VaR", money(summary["var"]))
    c2.metric("Expected Shortfall", money(summary["expected_shortfall"]))
    c3.metric("Mean loss", money(summary["mean_loss"]))
    c4.metric("Probability of loss", f"{summary['probability_positive_loss']*100:.1f}%")

    fig = px.histogram(sims, x="loss", nbins=60, title="Simulated loss distribution")
    fig.add_vline(x=summary["var"], line_dash="dash", annotation_text="VaR")
    fig.add_vline(x=summary["expected_shortfall"], line_dash="dot", annotation_text="ES")
    st.plotly_chart(fig, use_container_width=True)

    paths = simulate_vasicek_rates(r0, kappa, theta, sigma, horizon, max(4, int(12 * horizon)), 50, seed=1)
    path_df = pd.DataFrame(paths.T)
    path_df["step"] = path_df.index
    long = path_df.melt(id_vars="step", var_name="simulation", value_name="rate")
    fig2 = px.line(long, x="step", y="rate", color="simulation", title="Sample simulated rate paths")
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

elif page == "RAG Stress Assistant":
    st.title("Retrieval-Augmented Stress Testing Assistant")
    st.markdown(
        "This module retrieves relevant snippets from local public/synthetic notes and builds a structured scenario card. It is retrieval-augmented, but it does not train a model and does not require an external LLM API."
    )

    query = st.text_area(
        "Stress-testing query",
        value="Design an interest-rate and liquidity stress scenario for a fixed-income reserve portfolio.",
        height=100,
    )
    top_k = st.slider("Retrieved chunks", 2, 6, 4)

    if st.button("Run retrieval and generate scenario card"):
        chunks = retrieve(query, DOCS_DIR, top_k=top_k)
        card = generate_scenario_card(query, chunks)
        st.subheader("Scenario card")
        st.json(card)
        st.subheader("Retrieved evidence snippets")
        for r in chunks:
            with st.expander(f"{r.source} | chunk {r.chunk_id} | score {r.score:.3f}"):
                st.write(r.text)

elif page == "Agent-Based Stress Simulation":
    st.title("Agent-Based Market Liquidity Stress Simulator")
    st.markdown("A simplified ABM showing how heterogeneous behaviour and liquidity constraints can amplify market stress.")

    col1, col2, col3 = st.columns(3)
    with col1:
        n_steps = st.slider("Simulation steps", 30, 300, 120, 10)
        fundamental_volatility = st.slider("Fundamental volatility", 0.001, 0.02, 0.004, 0.001)
    with col2:
        price_impact = st.slider("Price impact", 0.001, 0.08, 0.018, 0.001)
        forced_sale_threshold = st.slider("Forced-sale drawdown threshold", -0.15, -0.005, -0.035, 0.005)
    with col3:
        forced_sale_intensity = st.slider("Forced-sale intensity", 0.05, 1.0, 0.45, 0.05)
        market_maker_capacity = st.slider("Market-maker stabilising capacity", 0.0, 0.9, 0.35, 0.05)

    settings = ABMSettings(
        n_steps=n_steps,
        fundamental_volatility=fundamental_volatility,
        price_impact=price_impact,
        forced_sale_threshold=forced_sale_threshold,
        forced_sale_intensity=forced_sale_intensity,
        market_maker_capacity=market_maker_capacity,
    )
    abm_df, diagnostics = simulate_market_stress(settings)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total P&L", money(diagnostics["total_pnl"]))
    c2.metric("Max drawdown", f"{diagnostics['max_drawdown']*100:.2f}%")
    c3.metric("Max spread proxy", f"{diagnostics['max_spread_proxy']:.4f}")
    c4.metric("Forced selling events", f"{diagnostics['forced_selling_events']:.0f}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=abm_df["step"], y=abm_df["price_index"], name="Price index"))
    fig.add_trace(go.Scatter(x=abm_df["step"], y=abm_df["spread_proxy"] * 10000, name="Spread proxy (scaled bps)", yaxis="y2"))
    fig.update_layout(
        title="ABM price and liquidity stress dynamics",
        yaxis=dict(title="Price index"),
        yaxis2=dict(title="Spread proxy, bps", overlaying="y", side="right"),
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.area(abm_df, x="step", y="forced_selling", title="Forced selling intensity")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(format_dataframe_numeric(abm_df.tail(20)), use_container_width=True)

elif page == "Governance and Limitations":
    st.title("Governance and Limitations")
    st.markdown(
        """
        ### Purpose
        This prototype demonstrates implementation ability and analytical reasoning. It is not a production risk engine.

        ### Data
        All data are synthetic. No confidential BIS, central-bank, market-desk, or employer data are used.

        ### Controls shown
        - transparent assumptions;
        - local reproducible retrieval instead of hidden model calls;
        - deterministic and stochastic stress outputs;
        - unit-testable pricing and risk functions;
        - explicit limitations and validation notes.

        ### Important limitations
        - no full term-structure calibration;
        - no real-time market data;
        - no credit, collateral, settlement, or counterparty-risk engine;
        - no production model validation;
        - ABM is stylised and designed for intuition, not calibration.

        ### Why this is still useful
        A good internship prototype should show the ability to translate a business/risk question into a clean analytical workflow, implement it reproducibly, expose assumptions, and communicate limitations clearly.
        """
    )
