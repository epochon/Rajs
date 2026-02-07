"""
Minimal FastAPI server for The Rational Decision Engine.
Exposes /api/analyze?ticker=SYMBOL, profiles, watchlist, and check-watchlist.
Run: uvicorn api:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from quant_tool import validate_ticker
from orchestrator import run_relay
from profiles import (
    create_profile as create_profile_store,
    delete_profile as delete_profile_store,
    get_profile as get_profile_store,
    list_profiles as list_profiles_store,
    update_profile_tickers,
)

app = FastAPI(title="Rational Decision Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# --- Request bodies ---
class CreateProfileBody(BaseModel):
    name: str


class UpdateTickersBody(BaseModel):
    add_tickers: list[str] | None = None
    remove_tickers: list[str] | None = None


@app.get("/api/analyze")
def analyze(ticker: str, thesis: str = ""):
    """Run the relay for the given ticker. Only tickers that exist in yfinance can be analyzed."""
    ticker = (ticker or "").strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="ticker is required")
    try:
        ctx = run_relay(ticker, thesis)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "ticker": ctx.ticker,
        "bear_output": ctx.bear_output,
        "bull_output": ctx.bull_output,
        "quant_data": ctx.quant_data,
        "verdict": ctx.verdict,
    }


# --- Profiles ---
@app.get("/api/profiles")
def list_profiles():
    """List all profiles (id, name, tickers)."""
    return list_profiles_store()


@app.post("/api/profiles")
def create_profile(body: CreateProfileBody):
    """Create a new profile with empty watchlist."""
    return create_profile_store(body.name or "Unnamed profile")


@app.get("/api/profiles/{profile_id}")
def get_profile(profile_id: str):
    """Get a single profile by id."""
    p = get_profile_store(profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return p


@app.patch("/api/profiles/{profile_id}")
def patch_profile(profile_id: str, body: UpdateTickersBody):
    """Add or remove tickers from a profile's watchlist. Only tickers that exist in yfinance can be added."""
    add_tickers = body.add_tickers or []
    invalid = []
    for t in add_tickers:
        ticker = (t or "").strip().upper()
        if not ticker:
            continue
        ok, err = validate_ticker(ticker)
        if not ok:
            invalid.append(f"{ticker}: {err}")
    if invalid:
        raise HTTPException(
            status_code=400,
            detail="Cannot add tickers not found in yfinance: " + "; ".join(invalid[:5])
            + (" …" if len(invalid) > 5 else ""),
        )
    p = update_profile_tickers(
        profile_id,
        add_tickers=body.add_tickers,
        remove_tickers=body.remove_tickers,
    )
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return p


@app.delete("/api/profiles/{profile_id}")
def delete_profile(profile_id: str):
    """Delete a profile."""
    if not delete_profile_store(profile_id):
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"ok": True}


@app.post("/api/profiles/{profile_id}/check-watchlist")
def check_watchlist(profile_id: str):
    """
    Run the AI analysis (Bear/Bull/Quant/Judge) for each ticker in the profile's watchlist.
    Returns per-ticker results and highlights which tickers have a BUY verdict (good time to invest).
    """
    p = get_profile_store(profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    tickers = [t for t in (p.get("tickers") or []) if (t or "").strip()]
    if not tickers:
        return {
            "profile_id": profile_id,
            "profile_name": p.get("name", ""),
            "results": [],
            "good_to_invest": [],
        }
    results = []
    good_to_invest = []
    for ticker in tickers:
        ticker = ticker.strip().upper()
        try:
            ctx = run_relay(ticker, "")
            verdict = ctx.verdict.get("verdict", "HOLD")
            results.append({
                "ticker": ctx.ticker,
                "verdict": verdict,
                "confidence_score": ctx.verdict.get("confidence_score", 0),
                "justification": ctx.verdict.get("justification", []),
                "quant_data": ctx.quant_data,
            })
            if verdict == "BUY":
                good_to_invest.append(ctx.ticker)
        except ValueError as e:
            results.append({
                "ticker": ticker,
                "verdict": "HOLD",
                "confidence_score": 0,
                "justification": [str(e)],
                "quant_data": {},
            })
        except Exception as e:
            results.append({
                "ticker": ticker,
                "verdict": "HOLD",
                "confidence_score": 0,
                "justification": [f"Analysis failed: {e!s}"],
                "quant_data": {},
            })
    return {
        "profile_id": profile_id,
        "profile_name": p.get("name", ""),
        "results": results,
        "good_to_invest": good_to_invest,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
