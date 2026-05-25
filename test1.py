from qc import quantconnect
from requests import post
import os
from dotenv import load_dotenv
import json
import re
import datetime as dt
import db.update_row as ur

load_dotenv()

qc = quantconnect


def get_log() -> dict:
    payload = {
        'projectId': os.getenv('PROJECT_ID'),
        'algorithmId': os.getenv('ALGO_ID'),
        'startLine': 1248,
        'endLine': 1251,
        "deploymentLogs": True
    }

    response = post(f'{qc.BASE_URL}/live/logs/read',
                    headers=qc.get_headers(), json=payload)

    content = response.json()

    # clean_content = json.dumps(content, indent=2)

    # with open('test1-logs.json', 'w') as j:
    #     j.write(clean_content)

    return content
    # # Log length = 800, get the last 200, endLine - 200 = startline
    # # Then we have the startline and end line to make the request for the last 200 logs


def parse_data() -> dict:
    logs = get_log()['logs']
    status = logs[0]
    state = logs[1].split("|")
    values = logs[2].split('|')
    
    # logs = json.dumps(logs, indent=2)

    # with open('test1-logs.json', 'w') as l:
    #     l.write(logs)
    
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
            1].strip() for item in logs if ":" in item if ':' in item}
        
        # result1 = json.dumps(result, indent=2)

        # with open('test1-logs.json', 'w') as t:
        #     t.write(result1)

        return result

    def parse_values() -> dict:

        value_list = [value.strip(" ") for value in values]

        # Replace with: result = {value.split(":", 1)[0].strip():int(value.split(":", 1)[1].lstrip(" $")) for value in value_list if ":" in value}
        result = {value.split(":", 1)[0].strip(): value.split(
            ":", 1)[1].lstrip(" $") for value in value_list if ":" in value}

        result1 = json.dumps(result, indent=2)

        return result

    db_datetime = dt.datetime.strptime(datetime_parse(), "%Y-%m-%d %H:%M:%S")
    db_algo_state = parse_state()
    db_values = parse_values()

    return db_algo_state


# def add_to_db():
#     '''
#     Map all values to appropriate cols in the db.

#     Need a session, commit, close session
#     '''

#     date, values, state = parse_data()

#     ur.populate_chart(date, values.get('Open'), values.get(
#         'High'), values.get('Low'), values.get('Close'))

#     return values

#     # ur.populate_chart(date, )


if __name__ == "__main__":
    # print(type(get_log_data()))
    # for log in parse_data():
    #     print(f"\n{log}")

    # print(parse_data())
    # print(parse_data())
    # print(json.dumps(get_log_data(), indent=4))

    print(type(parse_data()))
    # print(get_log())

    # add_to_db()
