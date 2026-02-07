"""
Sequential Relay Orchestrator for The Rational Decision Engine.
Execution order: Bear → Bull → Quant (data) → Rule-based Judge.
Verdict is deterministic from quant data; no LLM for final verdict.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from agents import (
    run_bear_agent,
    run_bear_bull_combined,
    run_bull_agent,
    run_lite_debate,
)
from config import COMBINED_DEBATE, LITE_MODE
from quant_tool import fetch_market_data

# --- Rule-based verdict (deterministic scoring) ---
# Score 0–100. Start at 50. Growth adds; high valuation/volatility/missing data subtract.
# >=70 BUY, 40–69 HOLD, <40 SELL.


def _n(val: Any) -> float | None:
    """Numeric value or None if N/A or invalid."""
    if val is None or val == "N/A":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def compute_rule_based_verdict(quant_data: dict[str, Any]) -> dict[str, Any]:
    """
    Deterministic verdict from quant data only.
    Returns: verdict (BUY|HOLD|SELL), confidence_score (0–100), justification (list), confidence_basis (str).
    """
    score = 50.0
    justification: list[str] = []
    na_count = 0

    # Revenue growth YoY (yfinance often N/A)
    rev = _n(quant_data.get("revenue_growth_yoy_pct"))
    if rev is not None:
        if rev > 0:
            add = min(15, rev / 2)
            score += add
            justification.append(f"Revenue growth YoY +{rev}% adds support (+{add:.0f} pts).")
        else:
            score -= 5
            justification.append(f"Revenue growth YoY {rev}% is not positive (-5 pts).")
    else:
        na_count += 1
        score -= 5
        justification.append("Revenue growth YoY not available; score penalized (-5 pts).")

    # EPS growth (yfinance often N/A)
    eps = _n(quant_data.get("eps_growth_pct"))
    if eps is not None:
        if eps > 0:
            add = min(10, eps / 3)
            score += add
            justification.append(f"EPS growth +{eps}% adds support (+{add:.0f} pts).")
        else:
            score -= 5
            justification.append(f"EPS growth {eps}% not positive (-5 pts).")
    else:
        na_count += 1
        score -= 5
        justification.append("EPS growth not available; score penalized (-5 pts).")

    # 30-day return
    ret30 = _n(quant_data.get("return_30d_pct"))
    if ret30 is not None:
        if ret30 > 0:
            add = min(10, ret30)
            score += add
            justification.append(f"30-day return +{ret30}% adds support (+{add:.0f} pts).")
        else:
            sub = min(10, abs(ret30))
            score -= sub
            justification.append(f"30-day return {ret30}% subtracts points (-{sub:.0f} pts).")
    else:
        na_count += 1
        score -= 5
        justification.append("30-day return not available; score penalized (-5 pts).")

    # 52-week range position (0 = at low, 1 = at high)
    pos52 = _n(quant_data.get("range_52w_position"))
    if pos52 is not None:
        if pos52 > 0.8:
            score -= 5
            justification.append(f"Price near 52w high (position {pos52:.2f}); valuation stretched (-5 pts).")
        elif pos52 < 0.2:
            score += 5
            justification.append(f"Price near 52w low (position {pos52:.2f}); relative value (+5 pts).")
    else:
        na_count += 1

    # High P/E subtracts
    pe = _n(quant_data.get("pe_ratio"))
    if pe is not None:
        if pe > 80:
            score -= 20
            justification.append(f"High P/E ({pe:.0f}) significantly reduces score (-20 pts).")
        elif pe > 50:
            score -= 15
            justification.append(f"High P/E ({pe:.0f}) reduces score (-15 pts).")
        elif pe > 30:
            score -= 10
            justification.append(f"Elevated P/E ({pe:.0f}) reduces score (-10 pts).")
    else:
        na_count += 1
        score -= 5
        justification.append("P/E not available; valuation certainty reduced (-5 pts).")

    # High volatility subtracts
    vol = _n(quant_data.get("volatility_proxy"))
    if vol is not None:
        if vol > 0.7:
            score -= 15
            justification.append(f"High volatility ({vol:.2f}) reduces score (-15 pts).")
        elif vol > 0.5:
            score -= 10
            justification.append(f"Elevated volatility ({vol:.2f}) reduces score (-10 pts).")
    else:
        na_count += 1
        score -= 5
        justification.append("Volatility not available; uncertainty penalized (-5 pts).")

    # Additional penalty for many missing metrics (data unreliability)
    if na_count >= 4:
        score -= 10
        justification.append(f"Many metrics missing ({na_count}); data completeness low (-10 pts).")

    score = max(0.0, min(100.0, round(score, 0)))
    confidence_score = int(score)

    if score >= 70:
        verdict = "BUY"
    elif score >= 40:
        verdict = "HOLD"
    else:
        verdict = "SELL"

    # Confidence basis: data completeness, volatility, valuation certainty
    completeness = "low" if na_count >= 4 else ("medium" if na_count >= 2 else "high")
    vol_label = "high" if vol is not None and vol > 0.5 else ("medium" if vol is not None else "unknown")
    valuation_certainty = "P/E available" if pe is not None else "P/E unavailable"
    confidence_basis = (
        f"Data completeness: {completeness} ({7 - na_count}/7 key metrics). "
        f"Volatility: {vol_label}. "
        f"Valuation certainty: {valuation_certainty}."
    )

    return {
        "verdict": verdict,
        "confidence_score": confidence_score,
        "justification": justification,
        "confidence_basis": confidence_basis,
    }


@dataclass
class RelayContext:
    """Context passed along the relay."""
    ticker: str
    thesis: str
    bear_output: str = ""
    bull_output: str = ""
    quant_data: dict[str, Any] = field(default_factory=dict)
    quant_json: str = ""
    market_data_missing: bool = True
    verdict: dict[str, Any] = field(default_factory=dict)


def run_relay(ticker: str, thesis: str = "") -> RelayContext:
    """
    Execute the relay: Bear → Bull → Quant → Rule-based Judge.
    Verdict is deterministic from quant data; Bear/Bull remain for narrative only.
    """
    ctx = RelayContext(ticker=ticker.strip(), thesis=(thesis or "").strip())

    ctx.quant_data = fetch_market_data(ctx.ticker)
    ctx.quant_json = json.dumps(ctx.quant_data, indent=2)
    ctx.market_data_missing = not ctx.quant_data.get("data_available", False)

    if LITE_MODE:
        ctx.bear_output, ctx.bull_output, _ = run_lite_debate(
            ctx.ticker, ctx.thesis, ctx.quant_json, ctx.market_data_missing
        )
    else:
        if COMBINED_DEBATE:
            ctx.bear_output, ctx.bull_output = run_bear_bull_combined(ctx.ticker, ctx.thesis)
        else:
            ctx.bear_output = run_bear_agent(ctx.ticker, ctx.thesis)
            ctx.bull_output = run_bull_agent(ctx.ticker, ctx.thesis, ctx.bear_output)

    # Deterministic verdict from quant data only (no LLM Judge)
    if ctx.market_data_missing:
        ctx.verdict = {
            "verdict": "HOLD",
            "confidence_score": 0,
            "justification": ["Insufficient market data; default verdict HOLD."],
            "confidence_basis": "Data completeness: none. Verdict not reliable.",
        }
    else:
        ctx.verdict = compute_rule_based_verdict(ctx.quant_data)

    return ctx


def format_report(ctx: RelayContext) -> str:
    """Human-readable report: verdict, confidence, bullet justification, confidence basis, disclaimer."""
    v = ctx.verdict
    verdict = v.get("verdict", "HOLD")
    confidence = v.get("confidence_score", 0)
    justification = v.get("justification", [])
    confidence_basis = v.get("confidence_basis", "")
    bullets = "\n".join(f"  • {j}" for j in justification) if justification else "  (none)"

    disclaimer = (
        "This output is for decision support only and does not constitute financial advice. "
        "Do your own research and consider consulting a licensed advisor."
    )

    lines = [
        "=" * 60,
        "THE RATIONAL DECISION ENGINE — Decision Report",
        "=" * 60,
        f"Ticker: {ctx.ticker}",
        f"Thesis: {ctx.thesis or '(none)'}",
        "",
        "--- Risk Analyst (Bear) ---",
        ctx.bear_output,
        "",
        "--- Growth Advocate (Bull) ---",
        ctx.bull_output,
        "",
        "--- Quantitative Data ---",
        ctx.quant_json,
        "",
        "--- Verdict ---",
        f"Verdict: {verdict}",
        f"Confidence score: {confidence} (0–100)",
        "",
        "Justification:",
        bullets,
        "",
        "Confidence basis:",
        f"  {confidence_basis}",
        "",
        "--- Disclaimer ---",
        disclaimer,
        "",
        "=" * 60,
    ]
    return "\n".join(lines)
