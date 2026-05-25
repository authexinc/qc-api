from requests import post
from . import quantconnect as qc
import json
import logging
import re
from dotenv import load_dotenv
import os
import datetime as dt
import db.update_row as ur


load_dotenv()


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
        response = post(f'{qc.BASE_URL}/live/logs/read',
                        headers=qc.get_headers(), json=payload)

        content = response.json()

        return content

    init_content = init_request()

    def log_len(contains) -> int:
        int_len = contains.get('length')  # Returns 88
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


def parse_data() -> dict:
    logs = get_log()['logs'].split("#")
    status = logs[0]
    state = logs[1].split("|")
    values = logs[2].split('|')

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

    db_datetime = dt.datetime.strptime(datetime_parse(), "%Y-%m-%d %H:%M:%S")
    db_algo_state = parse_state()
    db_values = parse_values()

    return db_datetime, db_values, db_algo_state


def add_to_db():
    '''
    Map all values to appropriate cols in the db.
    '''

    date, values, state = parse_data()

    ur.populate_chart(date, float(values.get('Open')), float(values.get(
        'High')), float(values.get('Low')), float(values.get('Close')), int(values.get('Volume')),
        float(values.get('EMA_1min')), float(
        values.get('EMA_Middle')),
        float(values.get('MTE1')), float(values.get('MTE2')), float(values.get(
            'MTE3')), float(values.get('MTE4')), float(values.get("EMA_10min_200")),
        float(values.get('LTE1')), float(values.get("LTE2")), float(values.get(
            'MTE1_L10')), float(values.get("MTE1_L9")), float(values.get('MTE1_L8')),
        float(values.get('MTE1_L7')), float(values.get('MTE1_L6')), float(values.get(
            'MTE1_L5')), float(values.get("MTE1_L4")), float(values.get("MTE1_L3")),
        float(values.get("MTE1_L2")), float(
        values.get("MTE1_L1")), float(values.get("MTE4_L5")), float(values.get("MTE4_L4")),
        float(values.get("MTE4_L3")), float(
        values.get("MTE4_L2")), float(values.get("MTE4_L1")), float(values.get(
            "MTE4_L0")), float(values.get("MTE4_-L1")),
        float(values.get("MTE4_-L2")), float(values.get("MTE4_-L3")),
        float(values.get("MTE4_-L4")), float(values.get("MTE4_-L5")
                                             ), float(values.get("EMA_1min_A")),
        float(values.get("EMA_Middle_A")), float(values.get(
            "EMA_4min_100_A")), float(values.get("EMA_4min_300_A")),
        float(values.get('EMA_!min_60')), float(values.get(
            "EMA_3min_80")), float(values.get('EMA_4min_100')),
        float(values.get("EMA_4min_200")), float(values.get("EMA_4min_300")))

    # Need to add proper type conversions when logs start coming in
    '''
    state_: str, gap_: str, strategy_:
    str, cmte_type_: str, cmte_val_: float, next_mte_: str, next_mte_val_: float,
    current_bie_val_: float, main_flow_state_: str, highest_sl_ema_type_: str,
    highest_sl_ema_val_: float, one_min_high_val_: float, one_min_high_G_: float,
    debs_main_buy_ok_: str, debs_main_sell_ok_: str, ema2min_buy_state_: str,
    ema2min_sell_state_: str, gap_up_ema_: float, gap_down_ema_: float,
    gbp_: float, gsp_: float, invested_: str
    '''

    ur.populate_algo_state(
        date, state.get("State"), state.get("Gap"), state.get("Strategy"),
        state.get("Current_MTE_Type"), state.get("Current_MTE_Val"),
        state.get("Next_MTE"), state.get(
            "Next_MTE_Val"), state.get("Current_BIE_Val"),
        state.get("MainFlowState"), state.get("Highest_SL_EMA_Type"),
        state.get("Highest_SL_EMA_Val"), state.get("One_Min_High"),
        state.get("One_Min_High_G"), state.get("DEBS_Main_Buy_OK"),
        state.get("DEBS_Main_Sell_OK"), state.get("EMA2min_Buy_State"),
        state.get("EMA2min_Sell_State"), state.get("Gap_UP_EMA"),
        state.get("Gap_Down_EMA"), state.get(
            "GBP"), state.get("GSP"), state.get("Invested")
    )

    # Need a table for state information and link by timestamp


def chart_log_data():
    pass

if __name__ == "__main__":
    # print(type(get_log_data()))
    # for log in parse_data():
    #     print(f"\n{log}")

    # print(parse_data())
    # print(parse_data())
    # print(json.dumps(get_log_data(), indent=4))

    # print(parse_data())

    # print(get_log())
    add_to_db()
