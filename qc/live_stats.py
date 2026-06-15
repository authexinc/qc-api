from . import quantconnect as qc
from requests import post
from dotenv import load_dotenv
import os
import json

load_dotenv()


def live_stats() -> dict:
    payload = {
        'projectId':os.getenv('PROJECT_ID')
    }
    
    response = post(f'{qc.BASE_URL}/live/read', headers=qc.get_headers(), json=payload)
    
    return response.json()
    
    # with open('test10-logs.json', 'w') as l:
    #     l.write(json.dumps(result['runtimeStatistics'], indent=2))


if __name__ == "__main__":
    print(live_stats()['runtimeStatistics'])