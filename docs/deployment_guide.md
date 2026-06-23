# Deployment Guide

## Local deployment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud deployment

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the repository.
4. Use `app.py` as the app entry point.
5. Deploy.

No secrets are required.

## Recommended public repository settings

- Repository name: `central-bank-risk-analytics-prototypes`
- Description: `Fixed-income analytics, RAG stress testing, and agent-based market-stress simulation prototypes using public/synthetic data.`
- Topics: `fixed-income`, `risk-management`, `streamlit`, `stress-testing`, `monte-carlo`, `agent-based-modeling`, `rag`, `central-banking`
