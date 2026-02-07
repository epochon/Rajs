# Project: ArbiTicker

## Goal
To build a **deterministic, agentic finance system** that simulates a courtroom-style debate between AI agents to provide transparent, logic-driven investment analysis—moving beyond "black box" financial advice.

## Problem Statement
Retail investors often make emotional decisions or rely on opaque stock tips without understanding the underlying risks and growth factors. Current tools provide raw data but lack synthesis, while traditional AI models often hallucinate financial advice. **ArbiTicker** solves this by forcing a dialectic "Bear vs. Bull" debate grounded in real-time data, giving users a clear "glass box" view of the decision-making process.

## Key Features
- **Agentic Debate System:** Two distinct AI agents (Risk Analyst & Growth Advocate) powered by **Groq** argue the bear and bull cases for any given stock.
- **Deterministic Verdict Engine:** A rule-based "Judge" algorithm that weighs the AI arguments against live quantitative data to issue a strict BUY, HOLD, or SELL recommendation.
- **Live Market Data:** Integration with `yfinance` to fetch real-time price, volume, and fundamental data.
- **Watchlist Profiles:** Users can create custom profiles (e.g., "High Risk," "Tech Blue Chips") to batch-process and monitor multiple tickers simultaneously.
- **Transparent Reasoning:** Every verdict includes a generated summary of *why* the decision was made, citing specific risks and catalysts.

## Technical Stack
- **Frontend:** React, Vite, Node.js
- **Backend:** Python (FastAPI/Uvicorn)
- **AI Inference:** Groq API (Llama 3 / Mixtral)
- **Data Source:** yfinance API
- **Storage:** Local JSON (Lightweight profile management)
