from requests import post
from . import quantconnect as qh
from .live_stats import live_stats
import json
import logging
import re
from dotenv import load_dotenv, set_key
import os
import datetime as dt
import db.update_row as ur
from db.model import ChartData, Session, AlgoState
from sqlalchemy import select

load_dotenv()
path = '.env'


def clean_stat_float(val):
    if val is None:
        return None
    val_str = str(val).strip().replace('$', '').replace(',', '').replace('%', '').replace(' ', '')
    if val_str.lower() in ('none', 'null', '', 'idle'):
        return None
    try:
        return float(val_str)
    except ValueError:
        return None


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

    def get_deploy_id() -> str:
        payload = {
            "projectId": os.getenv('PROJECT_ID'),
            "status":"Running"
        }

        response = post(f"{qh.BASE_URL}/live/list", headers=qh.get_headers(), json=payload)
        
        result = response.json()['live'][0]['deployId']
        
        set_key(path, 'ALGO_ID', result)
            
        return result
    
    
    def init_request(startline=0, endline=1) -> str:  # Gets the log length
        payload = {
            'projectId': os.getenv('PROJECT_ID'),
            'algorithmId': get_deploy_id(),
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
            startline = 0

        startline = int(startline)

        return startline, int_len

    first, second = log_len(init_content)

    return init_request(first, second)

    # # Log length = 800, get the last 200, endLine - 200 = startline
    # # Then we have the startline and end line to make the request for the last 200 logs


def parse_data() -> list:
    logs = get_log()["logs"]
    log_list = []

    for log_str in logs:
        log = {re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ', '', entry.split("=")[0].strip()): entry.split("=", 1)[1].strip()
               for entry in log_str.split("#") if "=" in entry}

        log_list.append({
            'time': dt.datetime.strptime(log['time'], "%Y-%m-%d %H:%M:%S"),
            'open': log['open'],
            'high': log['high'],
            'low': log['low'],
            'close': log['close'],
            'volume': log['volume'],
            'ema_1min_6': log["ema_1min_60"],
            "ema_1min_60": log['ema_1min_60'],
            'ema_2min_60': log['ema_2min_60'],
            'ema_3min_80': log['ema_3min_80'],
            'ema_4min_100': log['ema_4min_100'],
            'ema_4min_200': log['ema_4min_200'],
            'ema_4min_300': log['ema_4min_300'],
            'ema_10min_200': log['ema_10min_200'],
            'ema_30min_750': log['ema_30min_750'],
            'ema_30min_2000': log['ema_30min_2000'],
            'ema_30min_2500': log['ema_30min_2500'],
            'mte1': log['mte1'],
            'mte2': log['mte2'],
            'mte3': log['mte3'],
            'mte4': log['mte4'],
            'lte1': log['lte1'],
            'lte2': log['lte2'],
            'ema_1min_6_a': log['ema_1min_6_a'],
            'ema_2min_60_a': log['ema_2min_60_a'],
            'ema_4min_100_a': log['ema_4min_100_a'],
            'ema_4min_300_a': log['ema_4min_300_a'],
            'one_min_high': log['one_min_high'],
            'buy_in_price': log['buy_in_price'],
            'sell_price': log['sell_price'],
            'one_min_high_g': log['one_min_high_g'],
            'gap_price': log['gap_price'],
            'current_state': log['current_state']
        })

    return log_list

# def parse_data() -> list:
#     # logs = get_log()['logs'].split("#")
#     logs = get_log()["logs"]
#     log_list = []

#     for log in logs:
#         logs_split = log.split("#")
#         status = logs_split[0]
#         state = logs_split[1].split("|")
#         values = logs_split[2].split('|')

#         def datetime_parse() -> str:

#             datetime_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'

#             match = re.search(datetime_pattern, status)

#             if match:
#                 # date = datetime.datetime.strptime(match.group(), "%Y-%m-%d")
#                 return match[1]
#             else:
#                 print("no datetime found")

#         def parse_state() -> dict:
#             logs = [log.strip(" ") for log in state]

#             result = {}
#             for item in logs:
#                 if ":" in item:
#                     k, v = item.split(":", 1)
#                     result[k.strip()] = v.strip()
#                 elif item.startswith("EMA2min_Sell_State"):
#                     result["EMA2min_Sell_State"] = item[len("EMA2min_Sell_State"):].strip()

#             return result

#         def parse_values() -> dict:
#             value_list = [value.strip(" ") for value in values]

#             result = {}
#             for value in value_list:
#                 if ":" in value:
#                     k, v = value.split(":", 1)
#                     result[k.strip()] = v.strip(" $")
#                 elif "$" in value:
#                     k, v = value.split("$", 1)
#                     result[k.strip()] = v.strip()

#             return result

#         log_list.append({
#             "datetime": dt.datetime.strptime(datetime_parse(), "%Y-%m-%d %H:%M:%S"),
#             # "datetime": datetime_parse(),
#             "state": parse_state(),
#             "values": parse_values(),
#         })

#     return log_list




def add_to_db():
    '''
    Map all values to appropriate cols in the db.
    '''
    for values in parse_data():
        
        session = Session()
        existing = session.execute(select(ChartData).where(
            ChartData.datetime == values['time'])).scalar_one_or_none()
        session.close()
        
        if existing:
            logging.info(f"Skipping duplicate row for {values['time']}")
            continue

        ur.populate_chart(
            values['time'],
            safe_float(values.get('open')),
            safe_float(values.get('high')),
            safe_float(values.get('low')),
            safe_float(values.get('close')),
            safe_int(values.get('volume')),
            safe_float(values.get('ema_1min_6')),
            safe_float(values.get('ema_2min_60')),
            safe_float(values.get('mte1')),
            safe_float(values.get('mte2')),
            safe_float(values.get('mte3')),
            safe_float(values.get('mte4')),
            safe_float(values.get("ema_10min_200")),
            safe_float(values.get('lte1')),
            safe_float(values.get("lte2")),
            safe_float(values.get("ema_1min_6_a")),
            safe_float(values.get("ema_2min_60_a")),
            safe_float(values.get("ema_4min_100_a")),
            safe_float(values.get("ema_4min_300_a")),
            safe_float(values.get("ema_1min_60")),
            safe_float(values.get("ema_3min_80")),
            safe_float(values.get('ema_4min_100')),
            safe_float(values.get("ema_4min_200")),
            safe_float(values.get("ema_4min_300")),
            safe_float(values.get('ema_30min_750')),
            safe_float(values.get('ema_30min_2000')),
            safe_float(values.get('ema_30min_2500'))
            
            )

        ur.populate_algo_state(
            values['time'],
            safe_float(values.get('one_min_high')),
            safe_float(values.get('buy_in_price')),
            safe_float(values.get('sell_price')),
            safe_float(values.get('one_min_high_g')),
            safe_float(values.get('gap_price')),
            safe_str(values.get('current_state'))

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
        AlgoState.datetime.desc())).scalars().all()
    result = []
    for row in rows:
        d = {col.name: getattr(row, col.name)
             for col in AlgoState.__table__.columns}
        d['datetime'] = d['datetime'].isoformat() if d.get('datetime') else None
        result.append(d)
    return result


def update_live_stats_db():
    try:
        stats_data = live_stats()
        if not stats_data or 'runtimeStatistics' not in stats_data:
            logging.warning("No runtimeStatistics returned from live_stats().")
            return
        
        stats = stats_data['runtimeStatistics']
        now = dt.datetime.now()
        
        ur.populate_live_stats(
            datetime_=now,
            equity_=clean_stat_float(stats.get('Equity')),
            fees_=clean_stat_float(stats.get('Fees')),
            holdings_=clean_stat_float(stats.get('Holdings')),
            net_profit_=clean_stat_float(stats.get('Net Profit')),
            sharpe_ratio_=clean_stat_float(stats.get('Probabilistic Sharpe Ratio')),
            return_pct_=clean_stat_float(stats.get('Return')),
            unrealized_=clean_stat_float(stats.get('Unrealized')),
            volume_=clean_stat_float(stats.get('Volume'))
        )
        logging.info(f"Successfully saved live stats to database at {now}")
    except Exception as e:
        logging.error(f"Error updating live stats database: {e}")


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