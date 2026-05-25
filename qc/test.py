from requests import post, get
# import qc.quantconnect as qc
import quantconnect as qc
import json
import algo_actions as aa
from dotenv import load_dotenv
import os

load_dotenv()

def init_request(startline=1250, endline=1251) -> str:  # Gets the log length
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
        
    with open('log1.json', 'w') as l:
        json.dump(content, l, sort_keys = True, indent = 4,
               ensure_ascii = False)
        
    # returns: {'logs': ['Algorithm Initialization: Paper Brokerage account base currency: USD'], 'length': 88, 'deploymentOffset': 0, 'success': True}
    return content

# print(json.dumps(init_request(), indent=2))

# print(type(init_request()))

init_request()