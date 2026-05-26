from fastapi import FastAPI
from qc import quantconnect, log_data
from qc.algo_actions import LiveUpdate
import append_file.append as ap
from append_file.append import AppendValue

qc, ld = quantconnect, log_data

app = FastAPI()
live_update = AppendValue()
lu = LiveUpdate()


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
