# The Rational Decision Engine

A **deterministic, agentic finance system** that simulates a courtroom-style debate before issuing any investment recommendation. The system does **not** provide direct financial advice; it produces a **transparent decision process**.

**LLMs: Groq and DeepSeek only** (no Gemini, no Claude).

---

## How to run on your laptop (step by step)

Assume you’re on **Windows**. You need **Python**, **Node.js**, and an **API key** (Groq or DeepSeek).

### Step 1: Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download **Python 3.11 or 3.12**.
2. Run the installer.
3. **Important:** On the first screen, check **“Add Python to PATH”**, then click **Install Now**.
4. Close and reopen any terminal (PowerShell or Command Prompt) so `python` is recognized.

Check: open a new terminal and run:

```powershell
python --version
```

You should see something like `Python 3.11.x` or `Python 3.12.x`.

### Step 2: Install Node.js

1. Go to [nodejs.org](https://nodejs.org/) and download the **LTS** version.
2. Run the installer (default options are fine).
3. Close and reopen your terminal.

Check:

```powershell
node --version
npm --version
```

You should see version numbers (e.g. `v20.x.x` and `10.x.x`).

### Step 3: Get an API key

The app uses an AI provider. You need **one** of these:

- **Groq (free tier):** Go to [console.groq.com](https://console.groq.com/), sign up, open **API Keys**, create a key, and copy it.
- **DeepSeek:** Go to [platform.deepseek.com](https://platform.deepseek.com/), sign up, create an API key, and copy it.

Keep the key somewhere safe (you’ll paste it in the next step).

### Step 4: Open the project folder in a terminal

1. Open **File Explorer** and go to the folder that contains this project (e.g. `C:\College\r4shh\r4shh`).
2. In the address bar, type `cmd` or `powershell` and press Enter. A terminal will open in that folder.

Or: open **PowerShell** or **Command Prompt**, then run:

```powershell
cd C:\College\r4shh\r4shh
```

(Replace with the actual path where your project lives.)

### Step 5: Create the `.env` file

1. In the same folder (`r4shh`), find the file **`.env.example`**.
2. Copy it and rename the copy to **`.env`** (no “.example”).
3. Open **`.env`** in Notepad or any editor.
4. Paste your API key:
   - If you use **Groq**, set:  
     `GROQ_API_KEY=your_groq_key_here`  
     and keep:  
     `LLM_PROVIDER=groq`
   - If you use **DeepSeek**, set:  
     `DEEPSEEK_API_KEY=your_deepseek_key_here`  
     and set:  
     `LLM_PROVIDER=deepseek`
5. Save and close the file.

### Step 6: Start the backend (first terminal)

In the terminal where you’re in `C:\College\r4shh\r4shh`, run these commands **one by one**:

```powershell
python -m venv .venv
```

Then activate the virtual environment (Windows):

```powershell
.venv\Scripts\activate
```

You should see `(.venv)` at the start of the line. Then:

```powershell
pip install -r requirements.txt
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Leave this terminal **open**. When it’s ready you’ll see something like: `Uvicorn running on http://0.0.0.0:8000`.

**If activate doesn’t work** (e.g. “The module '.venv' could not be loaded” or “uvicorn is not recognized”), use the venv’s Python directly (no activate needed):

```powershell
cd C:\College\r4shh\r4shh
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Start the frontend (second terminal)

1. Open a **new** terminal (PowerShell or Command Prompt).
2. Go to the project folder and into the `frontend` folder:

```powershell
cd C:\College\r4shh\r4shh\frontend
```

3. Install dependencies and start the app:

```powershell
npm install
npm run dev
```

Leave this terminal **open** too. You’ll see something like: `Local: http://localhost:5173/`.

### Step 8: Open the app in your browser

1. Open **Chrome**, **Edge**, or **Firefox**.
2. In the address bar type: **http://localhost:5173** and press Enter.

You should see **The Rational Decision Engine** page. You can:

- Enter a ticker (e.g. **AAPL** or **AMD**) and click **Analyze** to run the AI.
- Create a **profile**, add tickers to the **watchlist**, then click **Check watchlist** to see which get a BUY verdict.

**Important:** You must have **both** terminals running (backend + frontend). If the backend is not running, "Create profile" and "Add ticker" will do nothing; the app will show a red error like *"Backend not reachable"*. Profiles are saved in `data/profiles.json` inside the project folder; that file is created automatically when the backend runs and you use profiles.

### If something goes wrong

- **“python is not recognized”** → Install Python again and check **“Add Python to PATH”**; restart the terminal.
- **“npm is not recognized”** → Install Node.js and restart the terminal.
- **Backend errors about API key** → Check that `.env` is in the `r4shh` folder (same folder as `api.py`) and that `GROQ_API_KEY` or `DEEPSEEK_API_KEY` is set correctly.
- **Frontend can’t reach backend** → Make sure the first terminal is still running `uvicorn` and shows no errors.
- **Create profile / Add ticker does nothing** → The backend is not running. Start it in a terminal (Step 6). You should see a red message on the page if the backend is unreachable.
- **“No module named uvicorn”** → Dependencies weren’t installed in this venv. Run: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` from the project folder, then start uvicorn again.
- **Port already in use** → Another app is using port 8000 or 5173; close it or change the port in the command.

---

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

## Profiles and watchlist

- **Create profiles** — In the UI, create a profile (e.g. “Tech watchlist”) to group stocks you want the AI to track.
- **Add tickers** — Add symbols to a profile’s watchlist (e.g. AAPL, AMD, MSFT).
- **Check watchlist** — Click **Check watchlist (run AI analysis)**. The engine runs the Bear/Bull/Quant/Judge relay for each ticker and shows:
  - **Good time to invest** — tickers that get a **BUY** verdict (highlighted at the top).
  - **All results** — verdict and confidence for every ticker; click a ticker to see the full analysis.

Profiles and watchlists are stored in `data/profiles.json` (created automatically). This is for decision support only; it does not constitute financial advice.

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
