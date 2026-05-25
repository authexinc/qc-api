from qc import quantconnect
from requests import post
import os
from dotenv import load_dotenv
import json
import re

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

    clean_content = json.dumps(content, indent=2)

    with open('test1-logs.json', 'w') as j:
        j.write(clean_content)

    return content
    # # Log length = 800, get the last 200, endLine - 200 = startline
    # # Then we have the startline and end line to make the request for the last 200 logs


def parse_data() -> dict:

    logs = get_log()['logs'][2].split("|")

    clean_logs = [x.strip(" ") for x in logs]

    result = {log.split(":", 1)[0].strip(" "): log.split(
        ":", 1)[1].lstrip(' $') for log in clean_logs if ":" in log}

    result_json = json.dumps(result, indent=2)

    with open('final-logs.json', 'w') as f:
        f.write(result_json)

    return result



if __name__ == "__main__":
    
    print(parse_data())
