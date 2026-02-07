# The Rational Decision Engine

A **deterministic, agentic finance system** that simulates a courtroom-style debate before issuing any investment recommendation. The system does **not** provide direct financial advice; it produces a **transparent decision process**.

**LLM Provider: Groq** (High-speed inference).

---

## How to run (Step-by-Step)

Prerequisites: **Python (3.11+)**, **Node.js**, and a **Groq API Key**.

### Step 1: Get a Groq API Key

1.  Go to [console.groq.com](https://console.groq.com/).
2.  Sign up and go to **API Keys**.
3.  Create a new key and copy it.

### Step 2: Clone or Download the Repository

1.  Clone this repository or download the ZIP file and extract it.
2.  Open your terminal (Command Prompt, PowerShell, or Terminal).
3.  Navigate to the project folder:
    ```bash
    cd rational-decision-engine
    ```

### Step 3: Configure the Environment

1.  In the project root, find the file `.env.example`.
2.  Copy it and rename the copy to `.env`.
3.  Open `.env` in a text editor.
4.  Paste your API key:
    ```ini
    GROQ_API_KEY=gsk_your_key_here
    LLM_PROVIDER=groq
    ```
5.  Save the file.

### Step 4: Start the Backend

1.  Open a terminal in the project root.
2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
3.  Activate the virtual environment:
    * **Windows:**
        ```powershell
        .venv\Scripts\activate
        ```
    * **Mac/Linux:**
        ```bash
        source .venv/bin/activate
        ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Start the API server:
    ```bash
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
    ```
    *Keep this terminal open.*

### Step 5: Start the Frontend

1.  Open a **new** terminal window.
2.  Navigate to the `frontend` directory inside the project:
    ```bash
    cd frontend
    ```
3.  Install dependencies:
    ```bash
    npm install
    ```
4.  Start the development server:
    ```bash
    npm run dev
    ```
5.  You will see a local URL (usually `http://localhost:5173`). Open this in your browser.

---

## Usage

### Single Ticker Analysis
1.  Enter a stock ticker (e.g., `AAPL`, `NVDA`, `TSLA`) in the search bar.
2.  Click **Analyze**.
3.  The engine will trigger the agents (Bear & Bull) and the quantitative model to generate a transparent report.

### Watchlist & Profiles
1.  **Create Profile:** Create a named profile (e.g., "Tech Stocks") to group your interests.
2.  **Add Tickers:** Add symbols to that profile's watchlist.
3.  **Check Watchlist:** Click **Run AI Analysis**. The engine runs the full debate relay for every ticker in the list and highlights stocks with a **BUY** verdict.

*Note: Profiles are stored locally in `data/profiles.json`.*

---

## Architecture

1.  **Bear Agent (Risk Analyst):** Powered by Groq. Argues the downside case.
2.  **Bull Agent (Growth Advocate):** Powered by Groq. Argues the upside case.
3.  **Quant Tool:** Uses `yfinance` to fetch real-time market data.
4.  **The Judge:** A deterministic, rule-based system that weighs the arguments and data to output a strict verdict (BUY/HOLD/SELL).

If market data is missing or incomplete, the verdict defaults to **HOLD**.

## Troubleshooting

* **"Backend not reachable":** Ensure the Python terminal is running `uvicorn` and there are no errors.
* **"API Key Error":** Check your `.env` file to ensure `GROQ_API_KEY` is pasted correctly without spaces.
* **"Module not found":** Ensure you activated the virtual environment (`.venv`) before running `pip install`.

## Disclaimer

This project is a **simulation of a decision-making process**. It is for educational and research purposes only and does **not** constitute financial advice.
