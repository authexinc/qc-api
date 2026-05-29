import os
from requests import post
from dotenv import load_dotenv
from base64 import b64encode
from hashlib import sha256
from time import time

load_dotenv()

USER_ID = os.getenv('QC_USER_ID')
API_TOKEN = os.getenv('QC_API_KEY')
BASE_URL = os.getenv('BASE_URL')
PROJECT_ID = os.getenv('PROJECT_ID')
ALGO_ID = os.getenv('ALGO_ID')

def get_headers():
    timestamp = f'{int(time())}'
    time_stamped_token = f'{API_TOKEN}:{timestamp}'.encode('utf-8')
    hashed_token = sha256(time_stamped_token).hexdigest()
    authentication = f'{USER_ID}:{hashed_token}'.encode('utf-8')
    authentication = b64encode(authentication).decode('ascii')
    return {
        'Authorization': f'Basic {authentication}',
        'Timestamp': timestamp
    }

def init_request(startline=0, endline=1):
    payload = {
        'projectId': PROJECT_ID,
        'algorithmId': ALGO_ID,
        'startLine': startline,
        'endLine': endline,
        "deploymentLogs": True
    }
    response = post(f'{BASE_URL}/live/logs/read', headers=get_headers(), json=payload)
    return response.json()

print("Fetching initial log length...")
init_content = init_request()
int_len = int(init_content.get('length', 0))
print(f"Total log lines on QuantConnect: {int_len}")

if int_len > 200:
    first = int_len - 200
else:
    first = 0
second = int_len

print(f"Requesting logs from line {first} to {second}...")
final_content = init_request(first, second)

if final_content.get('success'):
    logs = final_content.get('logs', [])
    print(f"\nRetrieved {len(logs)} log lines.")
    print("\n=== LAST 15 RAW LOG LINES ===")
    for idx, log in enumerate(logs[-15:]):
        print(f"[-{15-idx}]: {repr(log)}")
else:
    print("API Error:", final_content)
