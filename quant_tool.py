"""
Quant Tool: Fetches real market data using yfinance.
Data only, no opinions. Returns JSON. Missing data reported as "N/A".
"""
import json
from typing import Any

try:
    import yfinance as yf
except ImportError:
    yf = None

# Volatility proxy: annualized standard deviation of daily log returns (252 trading days).
# Limitation: past volatility may not predict future; yfinance history can be stale or thin.
VOLATILITY_PROXY_DESCRIPTION = (
    "Annualized volatility: std of daily returns × sqrt(252). "
    "Source: 1Y price history from yfinance. Limitation: backward-looking only."
)


def fetch_market_data(ticker: str) -> dict[str, Any]:
    """
    Fetch quantitative metrics for a ticker. Returns JSON-serializable dict.
    Missing or unavailable fields are set to "N/A" (string) for clarity.
    """
    if not yf:
        return _empty_response(ticker, error="yfinance not installed")

    ticker = str(ticker).strip().upper()
    if not ticker:
        return _empty_response(ticker, error="empty ticker")

    try:
        obj = yf.Ticker(ticker)
        info = obj.info
        hist_1y = obj.history(period="1y")
        # Need ~30 trading days for 30d return; 1y gives 52w range
        hist_30d = obj.history(period="1mo") if hist_1y is not None and not hist_1y.empty else None
    except Exception as e:
        return _empty_response(ticker, error=str(e))

    # --- Price ---
    # Limitation: yfinance 'currentPrice' / 'regularMarketPrice' can be delayed or missing for some tickers.
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    if current_price is None and hist_1y is not None and not hist_1y.empty:
        current_price = float(hist_1y["Close"].iloc[-1])
    current_price = _num_or_na(current_price)

    # --- P/E (trailing) ---
    # Limitation: may be missing for negative earnings or certain instruments.
    pe_ratio = _num_or_na(info.get("trailingPE"))

    # --- Market cap ---
    market_cap = _num_or_na(info.get("marketCap"))

    # --- Revenue growth YoY ---
    # yfinance: 'revenueGrowth' if available (fiscal period over period). Often N/A for many tickers.
    revenue_growth_yoy = info.get("revenueGrowth")
    revenue_growth_yoy = _num_or_na(revenue_growth_yoy)
    if revenue_growth_yoy != "N/A" and isinstance(revenue_growth_yoy, (int, float)):
        revenue_growth_yoy = round(float(revenue_growth_yoy) * 100, 2)  # as percentage

    # --- EPS growth (YoY or TTM) ---
    # yfinance: 'earningsGrowth' sometimes present. Else we could derive from earnings; often N/A.
    eps_growth = info.get("earningsGrowth")
    eps_growth = _num_or_na(eps_growth)
    if eps_growth != "N/A" and isinstance(eps_growth, (int, float)):
        eps_growth = round(float(eps_growth) * 100, 2)  # as percentage

    # --- 30-day return ---
    # Limitation: requires at least 2 close prices in the last ~30 trading days; holidays can thin data.
    return_30d = None
    if hist_30d is not None and not hist_30d.empty and "Close" in hist_30d.columns and len(hist_30d) >= 2:
        first_close = float(hist_30d["Close"].iloc[0])
        last_close = float(hist_30d["Close"].iloc[-1])
        if first_close and first_close != 0:
            return_30d = round((last_close - first_close) / first_close * 100, 2)
    return_30d = _num_or_na(return_30d)

    # --- 52-week range position ---
    # Current price as fraction of 52w range: (price - low) / (high - low). 0 = at low, 1 = at high.
    # Limitation: requires 1y history; illiquid names may have gaps.
    range_52w_low = None
    range_52w_high = None
    range_52w_position = "N/A"
    if hist_1y is not None and not hist_1y.empty and "Close" in hist_1y.columns and "High" in hist_1y.columns and "Low" in hist_1y.columns:
        range_52w_high = float(hist_1y["High"].max())
        range_52w_low = float(hist_1y["Low"].min())
        price_for_range = current_price if isinstance(current_price, (int, float)) else (float(hist_1y["Close"].iloc[-1]) if len(hist_1y) else None)
        if price_for_range is not None and range_52w_high is not None and range_52w_low is not None and range_52w_high > range_52w_low:
            pos = (price_for_range - range_52w_low) / (range_52w_high - range_52w_low)
            range_52w_position = round(pos, 4)  # 0–1 scale
    elif isinstance(range_52w_position, str) and range_52w_position == "N/A":
        pass  # already N/A

    # --- Volatility proxy ---
    # Annualized std of daily returns. Limitation: assumes 252 trading days; thin history distorts.
    volatility_proxy = None
    if hist_1y is not None and not hist_1y.empty and "Close" in hist_1y.columns and len(hist_1y) > 1:
        returns = hist_1y["Close"].pct_change().dropna()
        if len(returns) > 0:
            volatility_proxy = float(returns.std() * (252 ** 0.5))
    volatility_proxy = _num_or_na(volatility_proxy)

    # Data available if we have at least price or one key metric
    data_available = (
        current_price != "N/A"
        or pe_ratio != "N/A"
        or market_cap != "N/A"
        or volatility_proxy != "N/A"
        or return_30d != "N/A"
    )

    out = {
        "ticker": ticker,
        "current_price": current_price,
        "pe_ratio": pe_ratio,
        "market_cap": market_cap,
        "revenue_growth_yoy_pct": revenue_growth_yoy,
        "eps_growth_pct": eps_growth,
        "return_30d_pct": return_30d,
        "range_52w_low": _num_or_na(range_52w_low),
        "range_52w_high": _num_or_na(range_52w_high),
        "range_52w_position": range_52w_position,
        "volatility_proxy": volatility_proxy,
        "volatility_proxy_description": VOLATILITY_PROXY_DESCRIPTION,
        "data_available": data_available,
    }
    return out


def _num(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _num_or_na(v: Any) -> float | str:
    """Return float if valid number, else 'N/A' for explicit missing data."""
    n = _num(v)
    return n if n is not None else "N/A"


def _empty_response(ticker: str, error: str = "") -> dict[str, Any]:
    return {
        "ticker": ticker or "?",
        "current_price": "N/A",
        "pe_ratio": "N/A",
        "market_cap": "N/A",
        "revenue_growth_yoy_pct": "N/A",
        "eps_growth_pct": "N/A",
        "return_30d_pct": "N/A",
        "range_52w_low": "N/A",
        "range_52w_high": "N/A",
        "range_52w_position": "N/A",
        "volatility_proxy": "N/A",
        "volatility_proxy_description": VOLATILITY_PROXY_DESCRIPTION,
        "data_available": False,
        "error": error,
    }


def quant_tool_json(ticker: str) -> str:
    """Return market data as a JSON string (data only, no interpretation)."""
    return json.dumps(fetch_market_data(ticker), indent=2)


def validate_ticker(ticker: str) -> tuple[bool, str]:
    """
    Check if ticker exists in yfinance and has market data.
    Returns (is_valid, error_message). If valid, error_message is empty.
    """
    data = fetch_market_data(ticker)
    if data.get("data_available"):
        return True, ""
    t = (ticker or "").strip().upper() or "?"
    err = data.get("error", "")
    return False, f"Ticker '{t}' not found or has no market data in yfinance" + (f": {err}" if err else "")
