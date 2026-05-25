import os
from dotenv import load_dotenv
from qc import quantconnect
from requests import post, get
import json
import logging

load_dotenv()

qc = quantconnect


def get_log_data() -> dict:
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

    return content
    # # Log length = 800, get the last 200, endLine - 200 = startline
    # # Then we have the startline and end line to make the request for the last 200 logs

def parse_data1() -> dict:
    # timestamp = get_log_data()['']
    # for log in logs:
    #     timestamp = re.findall(r'\d{4}-\d{2}-\d{2}', 'text')
    #     return timestamp

    logs = get_log_data()['logs'][0]
    split = logs.split('|')
    clean_logs = [x.strip(" ") for x in split]

    # final = json.dumps(clean_logs, indent=2)

    output = {item.split(':')[0]: item.split(':')[1] for item in clean_logs}

    log1 = get_log_data()['logs'][2]

    split1 = log1.split('|')
    clean_logs1 = [x.strip(' ') for x in split1]
    # output1 = {item.split(':')[0]: item.split(':')[1] for item in clean_logs1}

    # output = json.dumps(output, indent=2)

    # with open('logs-test.json', 'w') as l:
    #     l.write(output)

    return clean_logs1


def parse_data() -> list:
    logs = get_log_data()['logs']
    clean_logs = json.dumps(logs, indent=2)

    # with open('good_logs.json', 'w') as l:
    #     l.write(clean_logs)
    
    return logs

def format_data():
    
    log_data = parse_data()
    
    for log in log_data:
        # log = {item.split('|'): item.split('|') for item in log}
        # print(json.dumps(log, indent=2))
        print(log)


if __name__ == "__main__":
    # print(type(format_data()))
    # print(type(parse_data()))
    
    print(get_log_data())