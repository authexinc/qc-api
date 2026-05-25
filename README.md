# qc-log-api

A FastAPI service that bridges a live QuantConnect trading algorithm with external controls and persistent storage.

## What it does

- **Fetches live logs** from the QuantConnect API and parses OHLCV, EMA indicator values, and algorithm state
- **Persists bar data** to a PostgreSQL database (chart values + algo state per bar)
- **Controls the live algorithm** — start, stop, and liquidate via REST endpoints
- **Pushes parameter updates** to a Google Sheet that the algorithm reads each bar (MTE/STE overrides)

## Architecture

```
QuantConnect Live Algo
        │
        ▼
  qc/log_data.py        ← fetches + parses live logs
  qc/algo_actions.py    ← start / stop / liquidate calls
        │
        ▼
   main.py (FastAPI)    ← REST API layer
        │
   ┌────┴────┐
   ▼         ▼
db/model.py  append_file/append.py
(SQLAlchemy) (Google Sheets via gspread)
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/live/log-data` | Raw log data from QuantConnect |
| `GET` | `/live/parse` | Parsed log data (datetime, values, state) |
| `POST` | `/live/actions/update/mte/{mte}` | Set MTE override value |
| `POST` | `/live/actions/clear/mte` | Clear MTE override |
| `POST` | `/live/actions/update/ste/{ste}` | Set STE override value |
| `POST` | `/live/actions/clear/ste` | Clear STE override |
| `POST` | `/live/actions/start` | Start live algorithm |
| `POST` | `/live/actions/stop` | Stop live algorithm |
| `POST` | `/live/actions/liquidate` | Liquidate positions |

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `QC_USER_ID` | QuantConnect user ID |
| `QC_API_KEY` | QuantConnect API key |
| `PROJECT_ID` | QC project ID |
| `ALGO_ID` | Live algorithm deployment ID |
| `BASE_URL` | QC API base URL |
| `INTERACTIVE_BROKERS_BROKERAGE_ID` | IBKR brokerage ID in QC |
| `IBKR_USER_NAME` | Interactive Brokers username |
| `IB_ACC_ID` | IB account number |
| `IB_PASSWORD` | IB password |
| `ENVIRONMENT` | `live` or `paper` |
| `POSTGRES` | SQLAlchemy connection string (e.g. `postgresql://user:pass@host/db`) |
| `DEPLOY_ID` | Live deployment ID |

### 3. Google Sheets credentials

Place your Google OAuth `credentials.json` in the project root (never commit this file). The sheet must be named `QC_PARAM` and shared with the service account.

### 4. Initialize the database

```bash
python db/model.py
```

### 5. Run the API

```bash
# Development (hot reload)
fastapi dev main.py

# Production
fastapi run main.py
```

API docs available at `http://localhost:8000/docs`.

## Project Structure

```
qc-log-api/
├── main.py               # FastAPI app and route definitions
├── qc/
│   ├── quantconnect.py   # Auth headers + QC API client
│   ├── log_data.py       # Log fetching, parsing, and DB writes
│   └── algo_actions.py   # Live algo control (start/stop/liquidate)
├── append_file/
│   └── append.py         # Google Sheets MTE/STE parameter updates
├── db/
│   ├── model.py          # SQLAlchemy models (ChartData, AlgoState)
│   └── update_row.py     # DB write helpers
├── .env.example          # Environment variable template
└── requirements.txt
```
