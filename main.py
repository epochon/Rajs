#!/usr/bin/env python3
"""
The Rational Decision Engine — CLI entrypoint.
Usage: python main.py <TICKER> [thesis]
Example: python main.py AAPL "Long-term hold on iPhone and services growth"
"""
import sys

from config import LLM_PROVIDER
from orchestrator import format_report, run_relay


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        print("Usage: python main.py <TICKER> [thesis]", file=sys.stderr)
        sys.exit(1)

    ticker = sys.argv[1]
    thesis = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"LLM provider: {LLM_PROVIDER} | Running relay: Bear → Bull → Quant → Judge...", file=sys.stderr)
    ctx = run_relay(ticker, thesis)
    print(format_report(ctx))


if __name__ == "__main__":
    main()
