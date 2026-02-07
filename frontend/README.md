# Rational Decision Engine — Frontend

Minimal hackathon demo UI: ticker input, Bear/Bull panels, quant charts, verdict.

## Run with backend (full stack)

**Terminal 1 — Python API**
```bash
cd c:\Users\amana\OneDrive\Desktop\r4shh
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

Open http://localhost:5173, enter a ticker (e.g. AMD), click **Analyze**. The UI calls `http://localhost:8000/api/analyze?ticker=...` for live data.

## Run frontend only (mock data)

If the API is not running, the app falls back to mock data automatically.

```bash
cd frontend
npm install
npm run dev
```

## API URL

Default: `http://localhost:8000`. Override with a `.env` in `frontend/`:

```
VITE_API_URL=http://localhost:8000
```

No auth, no routing, no deployment — runs locally only.
