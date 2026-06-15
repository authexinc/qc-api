from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from qc import quantconnect, log_data
from qc.algo_actions import LiveUpdate
import append_file.append as ap
from append_file.append import AppendValue

qc, ld = quantconnect, log_data

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdnjs.cloudflare.com/ajax/libs/redoc/2.1.3/redoc.standalone.js",
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
                logger.info(f"Trading hours: Running database update (update_live_stats_db)...")
                ld.update_live_stats_db()
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
    # Ensure database tables are created
    from db.model import Base, engine
    Base.metadata.create_all(bind=engine)
    
    thread = threading.Thread(target=trading_hours_scheduler, daemon=True)
    thread.start()


# ------ Get relevant info from db ------
# Replace these functions with db queries
# This will in turn both get persistent data and show us we are properly writing
# to db on every bar


@app.get("/live/log-data")
def get_log_data():
    return ld.get_log()


@app.get("/live/stats")
def get_live_stats():
    from qc.live_stats import live_stats
    return live_stats()


# @app.get('/live/parse')
# def parse_log_data() -> dict:
#     return ld.parse_data()


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
    return lu.start_live_algo()


@app.post('live/actions/liquidate')
def liquidate():
    lu.liquidate()


@app.post('/live/actions/stop')
def stop_algo():
    lu.stop_live_algo()
