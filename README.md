# QuantConnect Log API & Live Dashboard Service

A production-ready FastAPI service that bridges a live QuantConnect trading algorithm with external controls, persistent PostgreSQL storage, and real-time visualization on Grafana Cloud.

---

## System Architecture

```
                       ┌─────────────────────────┐
                       │  QuantConnect Live Algo │
                       └────────────┬────────────┘
                                    │ Live Logs & Controls
                                    ▼
                       ┌─────────────────────────┐
                       │      FastAPI App        │
                       │       (Port 8002)       │
                       └──────┬───────────┬──────┘
         CORS API Calls       │           │ Background Scheduler
         via Nginx Proxy      │           │ (Every 1 min during US Trading Hours)
     ┌────────────────────────┘           └────────────────────────┐
     ▼                                                             ▼
┌──────────────┐                                            ┌──────────────┐
│ Google Sheet │                                            │  PostgreSQL  │
│ (QC_PARAM)   │                                            │ (Port 5433)  │
└──────────────┘                                            └──────┬───────┘
                                                                   │ Tunneled securely via
                                                                   │ Grafana PDC Agent (SSH)
                                                                   ▼
                                                            ┌──────────────┐
                                                            │ Grafana Cloud│
                                                            │  Dashboard   │
                                                            └──────────────┘
```

---

## Features

1. **Live Log Fetching & Parsing:** Pulls live QuantConnect execution logs, parsing complex trading status parameters, indicator calculations, and OHLCV bars in real-time.
2. **Robust Storage:** Persists parsed bars into a native PostgreSQL instance with dual-table synchronization (`chart_values` for OHLCV & EMAs, `algo_state` for algorithm metadata) linked by datetime.
3. **Headless Google Sheets Integration:** Updates Google Sheets parameters (`MTE`/`STE` overrides) via `gspread` utilizing **lazy loading** to guarantee server startup success even if Google credentials are not yet initialized.
4. **US Trading Hours Background Scheduler:** Integrates an automatic, time-aligned background scheduler thread inside FastAPI that executes every minute during US stock market trading hours (Monday-Friday, 9:30 AM to 4:15 PM EST/EDT to catch buffered end-of-day logs).
5. **CORS-Enabled REST Controller:** Exposes secure control endpoints allowing external dashboards (like Grafana Cloud in the browser) to invoke start, stop, and liquidate operations.
6. **Grafana Cloud PDC Secure Tunnel:** Integrates with Grafana Private Data Source Connect (PDC) to securely expose the local PostgreSQL database to the cloud without opening external firewall ports.

---

## Complete REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/live/log-data` | Fetches raw log strings directly from QuantConnect API |
| `GET` | `/live/parse` | Returns live parsed logs (datetime, values, status dicts) |
| `GET` | `/live/chart` | Queries and returns all database OHLCV rows formatted as TradingView Unix JSON |
| `GET` | `/live/status` | Queries and returns recent algorithm metadata status as ISO-timestamped JSON |
| `GET` | `/live/orders` | Queries and returns the most recent order records from the database |
| `POST` | `/live/actions/update/mte/{mte}` | Triggers a Google Sheet cell update to override the MTE parameter |
| `POST` | `/live/actions/clear/mte` | Clears the Google Sheet MTE override parameter |
| `POST` | `/live/actions/update/ste/{ste}` | Triggers a Google Sheet cell update to override the STE parameter |
| `POST` | `/live/actions/clear/ste` | Clears the Google Sheet STE override parameter |
| `POST` | `/live/actions/start` | Starts the QuantConnect live algorithm |
| `POST` | `/live/actions/stop` | Safely stops the QuantConnect live algorithm |
| `POST` | `/live/actions/liquidate` | Liquidates all active brokerage positions on the live algorithm |

---

## File Structure

```
qc-api/
├── main.py                     # FastAPI controller, CORS configuration & trading hours scheduler
├── .env                        # Private environment secrets (never commit!)
├── requirements.txt            # Python dependencies
├── deploy.sh                   # One-click deployment shell script for the VPS
├── install-pdc.sh              # One-click Grafana PDC Agent installation script
├── grafana_dashboard.json      # Pre-built, ready-to-import Grafana dashboard definition
├── qc/
│   ├── quantconnect.py         # QuantConnect API headers & core request client
│   ├── log_data.py             # Log retrieval, regex parsing, and DB injection controllers
│   └── algo_actions.py         # Live trading algo start/stop/liquidate action wrappers
├── append_file/
│   └── append.py               # Google Sheets credentials & lazy gspread sheet updater
└── db/
    ├── model.py                # SQLAlchemy DB schema models (ChartData, AlgoState, LiveStats & Order)
    └── update_row.py           # DB insert / update helper functions
```

---

## Local Setup & Development

### 1. Clone & Environment Configuration
Ensure Python 3.10+ is installed. Set up the virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory (based on `.env.example`):
```ini
QC_USER_ID = 123456
QC_API_KEY = "your_quantconnect_api_key"
PROJECT_ID = 31331605
ALGO_ID = "L-your_live_algorithm_deployment_id"
BASE_URL = "https://www.quantconnect.com/api/v2/"
POSTGRES = "postgresql://qcuser:password@localhost:5432/qc_log"
```

### 2. Google credentials
Save your desktop OAuth client `credentials.json` (retrieved from Google Cloud Console) into the project root directory.

### 3. Initialize Database Tables
Create the local SQL tables:
```bash
python db/model.py
```

### 4. Running the Development Server
```bash
fastapi dev main.py
```
Your local FastAPI server will boot on port `8000`. You can test endpoints via `http://127.0.0.1:8000/docs`.

---

## Production VPS Deployment

For standard Linux VPS deployments where port `5432` and `8000` might have port conflicts (e.g. Docker platforms, Saleor installations, etc.), the production stack runs **FastAPI on Port 8002**, **PostgreSQL on Port 5433**, and proxies public traffic via **Nginx on Port 80**.

### 1. Database Initialization & Schema Permission
To fix PostgreSQL 15+ public schema permission blocks on your native VPS database:
```bash
# Connect to native psql on port 5433
sudo -u postgres psql -p 5433 -d qc_log -c "GRANT ALL ON SCHEMA public TO qcuser;"
sudo -u postgres psql -p 5433 -d qc_log -c "GRANT ALL PRIVILEGES ON DATABASE qc_log TO qcuser;"
```

### 2. One-Click Systemd & Nginx Deployment
We provide a unified deployment shell script. Running this script automates database migrations, sets up a systemd service, registers Nginx as a reverse proxy, and opens firewall ports:
```bash
bash /qc-api/deploy.sh
```

#### What `deploy.sh` Sets Up Under the Hood:
* **Systemd Service (`/etc/systemd/system/qc-log-api.service`):**
  Spawns FastAPI using Uvicorn locally on port `8002`:
  ```ini
  [Unit]
  Description=FastAPI QuantConnect Log API Service
  After=network.target postgresql.service

  [Service]
  User=root
  WorkingDirectory=/qc-api
  ExecStart=/qc-api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8002
  Restart=always
  RestartSec=5
  Environment=PATH=/qc-api/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

  [Install]
  WantedBy=multi-user.target
  ```

* **Nginx Site Configuration (`/etc/nginx/sites-available/qc-log-api`):**
  Sets up port 80 to reverse proxy directly to your local FastAPI server:
  ```nginx
  server {
      listen 80 default_server;
      listen [::]:80 default_server;
      server_name _;

      location / {
          proxy_pass http://127.0.0.1:8002;
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection 'upgrade';
          proxy_set_header Host $host;
          proxy_cache_bypass $http_upgrade;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```

* **UFW Firewall Rules:**
  Safely opens port 80:
  ```bash
  ufw allow 80/tcp
  ```

---

## Connecting to Grafana Cloud

### 1. Exposing the Database via PDC Agent
Rather than exposing your PostgreSQL server port `5433` publicly, run our automated Grafana PDC installation script on the VPS. This downloads the official `pdc-agent` and runs it securely in the background via systemd:

```bash
bash /qc-api/install-pdc.sh
```

The script registers a systemd service (`/etc/systemd/system/pdc-agent.service`) which connects to Grafana Cloud using a secure SOCKS5 SSH tunnel.

### 2. Adding the Database Data Source
In your Grafana Cloud console:
1. Go to **Connections** > **Data sources** > **Add new data source** > **PostgreSQL**.
2. Select your active **PDC Connection** under the network options.
3. Configure the host address to point to the local port:
   `localhost:5433`
4. Set credentials:
   - **Database:** `qc_log`
   - **User:** `qcuser`
   - **Password:** `autisticjose`
   - **SSL Mode:** `disable` (the connection is already fully encrypted inside the PDC agent tunnel)

### 3. Importing the Pre-Built Dashboard
1. Copy the contents of the pre-built [/qc-api/grafana_dashboard.json](file:///qc-api/grafana_dashboard.json) file.
2. In Grafana Cloud, go to **Dashboards** > **New** > **Import**.
3. Paste the JSON, select your registered **PostgreSQL Data Source**, set your VPS IP address in the button panel options, and click **Import**.

Your trading dashboard is now fully active, featuring a live **1-Min Candlestick & EMA Chart**, a **Metadata State Table**, and interactive **Start, Stop, and Liquidate Action Buttons**!
