from fastapi import FastAPI
from qc import quantconnect, log_data
from qc.algo_actions import LiveUpdate
import append_file.append as ap
from append_file.append import AppendValue

qc, ld = quantconnect, log_data

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
live_update = AppendValue()
lu = LiveUpdate()

import threading
import time
import datetime
import logging
from zoneinfo import ZoneInfo

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qc-scheduler")

def trading_hours_scheduler():
    logger.info("Trading hours scheduler thread started.")
    while True:
        try:
            # 1. Get current time in Eastern Time
            now_est = datetime.datetime.now(ZoneInfo("America/New_York"))
            
            # 2. Check if it's weekday (Monday=0 to Friday=4)
            is_weekday = now_est.weekday() < 5
            
            # 3. Check if time is between 9:30 AM and 4:00 PM EST
            start_time = datetime.time(9, 30, 0)
            end_time = datetime.time(16, 0, 0)
            is_trading_hours = start_time <= now_est.time() <= end_time
            
            if is_weekday and is_trading_hours:
                logger.info(f"Trading hours: Running database update (add_to_db)...")
                ld.add_to_db()
            else:
                logger.info(f"Skipping database update: Current time ({now_est.strftime('%Y-%m-%d %H:%M:%S %Z')}) is outside regular trading hours (Mon-Fri 9:30 AM - 4:00 PM EST).")
        except Exception as e:
            logger.error(f"Error in trading_hours_scheduler: {e}")
            
        # Sleep until the start of the next minute
        now = datetime.datetime.now()
        sleep_time = 60 - now.second - (now.microsecond / 1000000.0)
        time.sleep(sleep_time)

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=trading_hours_scheduler, daemon=True)
    thread.start()


# ------ Get relevant info from db ------
# Replace these functions with db queries
# This will in turn both get persistent data and show us we are properly writing
# to db on every bar


@app.get("/live/log-data")
def get_log_data():
    return ld.get_log_data()


@app.get('/live/parse')
def parse_log_data() -> dict:
    return ld.parse_data()


@app.get('/live/chart')
def chart_log_data():
    return ld.chart_log_data()


@app.get('/live/status')
def chart_status():
    return ld.chart_status()


# -------- CSTE/CMTE Updates ----------

# MTE Updates
@app.post('/live/actions/update/mte/{mte}')
def update_mte(mte):
    live_update.update_mte(mte)


@app.post('/live/actions/clear/mte')
def clear_mte():
    live_update.clear_mte()

# STE Updates


@app.post('/live/actions/update/ste/{ste}')
def update_ste(ste):
    live_update.update_ste(ste)


@app.post('/live/actions/clear/ste')
def clear_ste():
    live_update.clear_ste()


# -------- Algo actions ----------
@app.post('/live/actions/start')
def start_algo():
    lu.start_live_algo()


@app.post('live/actions/liquidate')
def liquidate():
    lu.liquidate()


@app.post('/live/actions/stop')
def stop_algo():
    lu.stop_live_algo()
