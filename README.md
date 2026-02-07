# The Rational Decision Engine

A **deterministic, agentic finance system** that simulates a courtroom-style debate before issuing any investment recommendation. The system does **not** provide direct financial advice; it produces a **transparent decision process**.

**LLMs: Groq and DeepSeek only** (no Gemini, no Claude).

## Quick start (CLI)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
# Set GROQ_API_KEY or DEEPSEEK_API_KEY in .env
python main.py AMD
```

## Quick start (API + frontend)

**Terminal 1 — Backend**
```bash
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and use the UI to analyze a ticker.

## Architecture

1. **Bear Agent** — Risk Analyst (Groq/DeepSeek)
2. **Bull Agent** — Growth Advocate (Groq/DeepSeek)
3. **Quant Tool** (yfinance) — Market data
4. **Rule-based Judge** — Deterministic verdict (BUY/HOLD/SELL) from quant only

If market data is missing, verdict defaults to **HOLD**.

## Setup

- Copy `.env.example` to `.env`. Set **GROQ_API_KEY** or **DEEPSEEK_API_KEY**.
- `LLM_PROVIDER=groq` or `deepseek`. Optional: `COMBINED_DEBATE=true`, `LITE_MODE=true` to reduce API calls.

## Disclaimer

This is a **simulation of a decision process**, not financial advice.
