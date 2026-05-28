from requests import post
from . import quantconnect as qh
import json
import logging
import re
from dotenv import load_dotenv
import os
import datetime as dt
import db.update_row as ur
from db.model import ChartData, Session, AlgoState
from sqlalchemy import select

load_dotenv()



def safe_float(val):
    if val is None:
        return None
    val_str = str(val).strip().replace('$', '').replace(' ', '')
    if val_str.lower() in ('none', 'null', '', 'idle'):
        return None
    try:
        return float(val_str)
    except ValueError:
        return None


def safe_int(val):
    if val is None:
        return None
    val_str = str(val).strip().replace('$', '').replace(' ', '')
    if val_str.lower() in ('none', 'null', '', 'idle'):
        return None
    try:
        return int(float(val_str))
    except ValueError:
        return None


def safe_bool(val):
    if val is None:
        return None
    val_str = str(val).strip().lower()
    if val_str in ('true', 't', 'y', 'yes', '1'):
        return True
    if val_str in ('false', 'f', 'n', 'no', '0'):
        return False
    return None


def safe_str(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in ('none', 'null', ''):
        return None
    return val_str


def get_log() -> dict:

    def init_request(startline=0, endline=1) -> str:  # Gets the log length
        payload = {
            'projectId': os.getenv('PROJECT_ID'),
            'algorithmId': os.getenv('ALGO_ID'),
            'startLine': startline,
            'endLine': endline,
            "deploymentLogs": True
        }
        # sample_payload = {
        #     "algorithmId": "L-321d891c57c3bf8c977462a31f51afe8",
        #     "start": startline,
        #     "end": endline,
        #     "projectId": 31331605
        # }
        response = post(f'{qh.BASE_URL}/live/logs/read',
                        headers=qh.get_headers(), json=payload)

        content = response.json()

        return content

    init_content = init_request()

    def log_len(contains) -> int:
        int_len = contains.get('length')  # Returns endLine
        int_len = int(int_len)

        if int_len > 200:
            startline = int_len - 200
        else:
            try:
                startline = (int_len / 2)
            except:
                if int_len == 0:
                    logging.info("Not enough insights yet.")
                    return 0, 0

        startline = int(startline)

        return startline, int_len

    first, second = log_len(init_content)

    return init_request(first, second)

    # # Log length = 800, get the last 200, endLine - 200 = startline
    # # Then we have the startline and end line to make the request for the last 200 logs


def parse_data() -> list:
    # logs = get_log()['logs'].split("#")
    logs = get_log()["logs"]
    log_list = []

    for log in logs:
        logs_split = log.split("#")
        status = logs_split[0]
        state = logs_split[1].split("|")
        values = logs_split[2].split('|')

        def datetime_parse() -> str:

            datetime_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'

            match = re.search(datetime_pattern, status)

            if match:
                # date = datetime.datetime.strptime(match.group(), "%Y-%m-%d")
                return match[1]
            else:
                print("no datetime found")

        def parse_state() -> dict:
            logs = [log.strip(" ") for log in state]

            result = {item.split(':', 1)[0].strip(): item.split(":", 1)[
                1].strip() for item in logs if ":" in item}

            return result

        def parse_values() -> dict:
            value_list = [value.strip(" ") for value in values]

            result = {value.split(":", 1)[0].strip(): value.split(
                ":", 1)[1].strip(" $") for value in value_list if ":" in value}

            return result

        log_list.append({
            "datetime": dt.datetime.strptime(datetime_parse(), "%Y-%m-%d %H:%M:%S"),
            # "datetime": datetime_parse(),
            "state": parse_state(),
            "values": parse_values(),
        })

    return log_list


def add_to_db():
    '''
    Map all values to appropriate cols in the db.
    '''
    for data in parse_data():
        
        date = data["datetime"]
        state = data['state']
        values = data['values']

        session = Session()
        existing = session.execute(select(ChartData).where(
            ChartData.datetime == date)).scalar_one_or_none()
        session.close()
        
        if existing:
            logging.info(f"Skipping duplicate row for {date}")
            return

        ur.populate_chart(
            date,
            safe_float(values.get('Open')),
            safe_float(values.get('High')),
            safe_float(values.get('Low')),
            safe_float(values.get('Close')),
            safe_int(values.get('Volume')),
            safe_float(values.get('EMA_1min')),
            safe_float(values.get('EMA_Middle')),
            safe_float(values.get('MTE1')),
            safe_float(values.get('MTE2')),
            safe_float(values.get('MTE3')),
            safe_float(values.get('MTE4')),
            safe_float(values.get("EMA_10min_200")),
            safe_float(values.get('LTE1')),
            safe_float(values.get("LTE2")),
            safe_float(values.get('MTE1_L10')),
            safe_float(values.get("MTE1_L9")),
            safe_float(values.get('MTE1_L8')),
            safe_float(values.get('MTE1_L7')),
            safe_float(values.get('MTE1_L6')),
            safe_float(values.get('MTE1_L5')),
            safe_float(values.get("MTE1_L4")),
            safe_float(values.get("MTE1_L3")),
            safe_float(values.get("MTE1_L2")),
            safe_float(values.get("MTE1_L1")),
            safe_float(values.get("MTE4_L5")),
            safe_float(values.get("MTE4_L4")),
            safe_float(values.get("MTE4_L3")),
            safe_float(values.get("MTE4_L2")),
            safe_float(values.get("MTE4_L1")),
            safe_float(values.get("MTE4_L0")),
            safe_float(values.get("MTE4_-L1")),
            safe_float(values.get("MTE4_-L2")),
            safe_float(values.get("MTE4_-L3")),
            safe_float(values.get("MTE4_-L4")),
            safe_float(values.get("MTE4_-L5")),
            safe_float(values.get("EMA_1min_A")),
            safe_float(values.get("EMA_Middle_A")),
            safe_float(values.get("EMA_4min_100_A")),
            safe_float(values.get("EMA_4min_300_A")),
            safe_float(values.get("EMA_1min_60") or values.get("EMA_!min_60")),
            safe_float(values.get("EMA_3min_80")),
            safe_float(values.get('EMA_4min_100')),
            safe_float(values.get("EMA_4min_200")),
            safe_float(values.get("EMA_4min_300"))
        )

        ur.populate_algo_state(
            date,
            safe_str(state.get("State")),
            safe_str(state.get("Gap")),
            safe_str(state.get("Strategy")),
            safe_str(state.get("Current_MTE_Type")),
            safe_float(state.get("Current_MTE_Val")),
            safe_str(state.get("Next_MTE")),
            safe_float(state.get("Next_MTE_Val")),
            safe_float(state.get("Current_BIE_Val")),
            safe_str(state.get("MainFlowState")),
            safe_str(state.get("Highest_SL_EMA_Type")),
            safe_float(state.get("Highest_SL_EMA_Val")),
            safe_float(state.get("One_Min_High")),
            safe_float(state.get("One_Min_High_G")),
            safe_bool(state.get("DEBS_Main_Buy_OK")),
            safe_bool(state.get("DEBS_Main_Sell_OK")),
            safe_str(state.get("EMA2min_Buy_State")),
            safe_str(state.get("EMA2min_Sell_State")),
            safe_float(state.get("Gap_UP_EMA")),
            safe_float(state.get("Gap_Down_EMA")),
            safe_float(state.get("GBP")),
            safe_float(state.get("GSP")),
            safe_bool(state.get("Invested"))
        )

    # Need a table for state information and link by timestamp


def chart_log_data() -> list[dict]:
    session = Session()
    rows = session.execute(select(ChartData).order_by(
        ChartData.datetime)).scalars().all()
    result = []
    for row in rows:
        d = {col.name: getattr(row, col.name)
             for col in ChartData.__table__.columns}
        d['time'] = int(d.pop('datetime').timestamp()
                        ) if d.get('datetime') else None
        result.append(d)
    return result


def chart_status() -> list[dict]:
    session = Session()
    rows = session.execute(select(AlgoState).order_by(
        AlgoState.datetime)).scalars().all()
    result = []
    for row in rows:
        d = {col.name: getattr(row, col.name)
             for col in AlgoState.__table__.columns}
        d['datetime'] = d['datetime'].isoformat() if d.get('datetime') else None
        result.append(d)
    return result


if __name__ == "__main__":
    # print(type(get_log_data()))
    # for log in parse_data():
    #     print(f"\n{log}")

    # print(parse_data())
    # print(json.dumps(get_log_data(), indent=4))

    # test = json.dumps(parse_data(), indent=2)
    # test = get_log()['logs']
    # print(parse_data()[0:3])
    # print(add_to_db())
    # test = json.dumps(parse_data(), indent=2)
    # with open('test6-logs.json', 'w') as t:
    #     t.write(test)
    
    # for data in parse_data():
    #     print(f'\n{data}')
    # print(parse_data())
    # print(get_log())
    # print(type(parse_data()))
    # print(type(parse_data()[0]['datetime']))
    add_to_db()

    # for data in parse_data():
    
    #     date = data["datetime"]
    #     state = data['state']
    #     values = data['values']
        
    #     print(date, state, values)    