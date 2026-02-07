"""
Agents for The Rational Decision Engine. Only Groq and DeepSeek (OpenAI-compatible).
"""
import json
from typing import Any

from config import (
    COMBINED_DEBATE,
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    LITE_MODE,
    LLM_PROVIDER,
)

# --- System prompts ---

BEAR_SYSTEM = """You are the Risk Analyst. List concrete downside risks only.

Rules:
- Categories: regulatory, valuation, competitive, macro.
- No conclusions or recommendations. No fabricated data.
- Data from public sources (e.g. yfinance) may be missing or delayed; do not invent numbers.
- Output: structured list of risks only. No preamble."""

BULL_SYSTEM = """You are the Growth Advocate. Argue upside while acknowledging risks.

Rules:
- First acknowledge the Bear (Risk Analyst) arguments given.
- Then counter with growth narratives/catalysts. No invented numbers.
- Public data (e.g. yfinance) may be N/A or delayed; only use numbers when provided.
- No conclusions or final recommendation. Concise and controlled."""

JUDGE_SYSTEM = """Synthesize Bear and Bull arguments and quantitative data. Output verdict as JSON only.
Rules: AVOID if existential risk dominates; BUY if strong growth with managed risk; HOLD if unclear.
Data may be incomplete (yfinance limitations). Output: {"verdict":"BUY"|"HOLD"|"AVOID","confidence_score":0-100,"reasoning":"..."}"""

BEAR_BULL_COMBINED_SYSTEM = """Two roles in one response.

1) Risk Analyst (Bear): list concrete downside risks only (regulatory, valuation, competitive, macro). No conclusions.
2) Growth Advocate (Bull): acknowledge those risks, then argue upside. No invented numbers. Data may be N/A from public sources.

Output exactly:
---RISKS---
(risk 1, risk 2, ...)
---BULL---
(bull response)
"""

LITE_SYSTEM = """One response: three parts for the given ticker and quantitative data.
Data may be incomplete (yfinance). Do not invent numbers.

1) RISKS: concrete downside risks only.
2) BULL: acknowledge risks, argue upside.
3) VERDICT: one JSON line: {"verdict":"BUY"|"HOLD"|"AVOID","confidence_score":0-100,"reasoning":"..."}

Output format:
---RISKS---
(risks)
---BULL---
(bull)
---VERDICT---
{...}
"""


def _call_openai_compatible(
    system: str,
    user_content: str,
    *,
    base_url: str,
    api_key: str,
    model: str,
) -> str:
    """Call Groq or DeepSeek (OpenAI-compatible). Returns raw text."""
    if not api_key:
        return "[API key not configured]"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        msg = client.chat.completions.create(
            model=model,
            max_tokens=2048,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
        )
        text = (msg.choices[0].message.content or "").strip()
        return text or "[Empty response]"
    except Exception as e:
        return f"[API error: {e}]"


def _call_llm(system: str, user_content: str, model_override: str | None = None) -> str:
    """Use LLM_PROVIDER: groq or deepseek. Fallback: if groq has no key, try deepseek."""
    if LLM_PROVIDER == "groq" and GROQ_API_KEY:
        return _call_openai_compatible(
            system, user_content,
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY,
            model=model_override or GROQ_MODEL,
        )
    if LLM_PROVIDER == "deepseek" and DEEPSEEK_API_KEY:
        return _call_openai_compatible(
            system, user_content,
            base_url="https://api.deepseek.com",
            api_key=DEEPSEEK_API_KEY,
            model=model_override or DEEPSEEK_MODEL,
        )
    # Fallback: try the other provider
    if GROQ_API_KEY:
        return _call_openai_compatible(
            system, user_content,
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY,
            model=model_override or GROQ_MODEL,
        )
    if DEEPSEEK_API_KEY:
        return _call_openai_compatible(
            system, user_content,
            base_url="https://api.deepseek.com",
            api_key=DEEPSEEK_API_KEY,
            model=model_override or DEEPSEEK_MODEL,
        )
    return "[No API key: set GROQ_API_KEY or DEEPSEEK_API_KEY in .env]"


def run_bear_agent(ticker: str, thesis: str = "") -> str:
    user = f"Ticker or investment: {ticker}"
    if thesis:
        user += f"\nContext or thesis: {thesis}"
    user += "\n\nList the concrete downside risks only."
    return _call_llm(BEAR_SYSTEM, user)


def run_bear_bull_combined(ticker: str, thesis: str) -> tuple[str, str]:
    user = f"Ticker or investment: {ticker}"
    if thesis:
        user += f"\nContext or thesis: {thesis}"
    raw = _call_llm(BEAR_BULL_COMBINED_SYSTEM, user)
    return _parse_bear_bull_combined(raw)


def _parse_bear_bull_combined(raw: str) -> tuple[str, str]:
    bear, bull = "", ""
    if "---RISKS---" in raw and "---BULL---" in raw:
        parts = raw.split("---BULL---", 1)
        risks_part = parts[0].split("---RISKS---", 1)[-1].strip()
        bull = parts[1].strip() if len(parts) > 1 else ""
        bear = risks_part
    else:
        bear = raw[: len(raw) // 2] if raw else "[No risks parsed]"
        bull = raw[len(raw) // 2 :] if raw else "[No bull parsed]"
    return bear or "[No risks]", bull or "[No bull response]"


def run_lite_debate(ticker: str, thesis: str, quant_json: str, market_data_missing: bool) -> tuple[str, str, dict[str, Any]]:
    if market_data_missing:
        return (
            "[Lite mode; no market data]",
            "[Lite mode; no market data]",
            {"verdict": "HOLD", "confidence_score": 0, "reasoning": "Market data missing. Default HOLD."},
        )
    user = f"Ticker: {ticker}\n"
    if thesis:
        user += f"Thesis: {thesis}\n"
    user += f"\nQuantitative data (use only this data, no inventing):\n{quant_json}"
    raw = _call_llm(LITE_SYSTEM, user)
    return _parse_lite_output(raw)


def _parse_lite_output(raw: str) -> tuple[str, str, dict[str, Any]]:
    bear = bull = ""
    verdict = _fallback_verdict("Lite: no verdict parsed")
    if "---VERDICT---" in raw:
        rest, verdict_block = raw.split("---VERDICT---", 1)
        verdict = _parse_judge_output(verdict_block.strip())
    else:
        rest = raw
    if "---RISKS---" in rest and "---BULL---" in rest:
        parts = rest.split("---BULL---", 1)
        bear = (parts[0].split("---RISKS---", 1)[-1].strip()) or "[No risks]"
        bull = (parts[1].strip() if len(parts) > 1 else "") or "[No bull]"
    else:
        bear = rest[: max(1, len(rest) // 2)] or "[No risks]"
        bull = rest[max(1, len(rest) // 2) :] or "[No bull]"
    return bear, bull, verdict


def run_bull_agent(ticker: str, thesis: str, bear_output: str) -> str:
    user = f"Ticker or investment: {ticker}"
    if thesis:
        user += f"\nContext or thesis: {thesis}"
    user += f"\n\n--- Risk Analyst (Bear) arguments you MUST acknowledge first ---\n{bear_output}\n\n---\nNow argue the upside and counter risks where appropriate. Do not invent numbers."
    return _call_llm(BULL_SYSTEM, user)


def run_judge_agent(
    ticker: str,
    bear_output: str,
    bull_output: str,
    quant_json: str,
    market_data_missing: bool,
) -> dict[str, Any]:
    if market_data_missing:
        return {
            "verdict": "HOLD",
            "confidence_score": 0,
            "reasoning": "Market data missing or unavailable. Per execution rules, default verdict is HOLD.",
        }

    user = f"""Ticker: {ticker}

--- Risk Analyst (Bear) ---
{bear_output}

--- Growth Advocate (Bull) ---
{bull_output}

--- Quantitative data (JSON, data only) ---
{quant_json}

---
Synthesize the above and output STRICT JSON only:
{{"verdict": "BUY" | "HOLD" | "AVOID", "confidence_score": <0-100>, "reasoning": "<explanation>"}}"""

    raw = _call_llm(JUDGE_SYSTEM, user)
    return _parse_judge_output(raw)


def _parse_judge_output(raw: str) -> dict[str, Any]:
    if not raw or raw.startswith("["):
        return _fallback_verdict(raw or "Empty response")

    stripped = raw.strip()
    for start in ("```json", "```"):
        if stripped.startswith(start):
            stripped = stripped[len(start) :].strip()
        if stripped.endswith("```"):
            stripped = stripped[:-3].strip()

    try:
        obj = json.loads(stripped)
    except json.JSONDecodeError:
        start_idx = stripped.find("{")
        if start_idx == -1:
            return _fallback_verdict(raw)
        depth = 0
        end_idx = -1
        for i in range(start_idx, len(stripped)):
            if stripped[i] == "{":
                depth += 1
            elif stripped[i] == "}":
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break
        if end_idx != -1:
            try:
                obj = json.loads(stripped[start_idx : end_idx + 1])
            except json.JSONDecodeError:
                return _fallback_verdict(raw)
        else:
            return _fallback_verdict(raw)

    verdict = (obj.get("verdict") or "").upper()
    if verdict not in ("BUY", "HOLD", "AVOID"):
        verdict = "HOLD"
    return {
        "verdict": verdict,
        "confidence_score": max(0, min(100, int(obj.get("confidence_score", 50)))),
        "reasoning": str(obj.get("reasoning", raw))[:2000],
    }


def _fallback_verdict(reason: str) -> dict[str, Any]:
    return {
        "verdict": "HOLD",
        "confidence_score": 0,
        "reasoning": f"Could not parse Judge output. Raw: {reason[:500]}",
    }
