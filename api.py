"""
Minimal FastAPI server for The Rational Decision Engine.
Exposes /api/analyze?ticker=SYMBOL for the frontend.
Run: uvicorn api:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from orchestrator import run_relay

app = FastAPI(title="Rational Decision Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/analyze")
def analyze(ticker: str, thesis: str = ""):
    """Run the relay for the given ticker. Returns JSON for the frontend."""
    ticker = (ticker or "").strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="ticker is required")
    try:
        ctx = run_relay(ticker, thesis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "ticker": ctx.ticker,
        "bear_output": ctx.bear_output,
        "bull_output": ctx.bull_output,
        "quant_data": ctx.quant_data,
        "verdict": ctx.verdict,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
