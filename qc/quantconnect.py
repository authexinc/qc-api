import os
from base64 import b64encode
from hashlib import sha256
from time import time
from requests import post
from dotenv import load_dotenv

environ = os.environ
load_dotenv()

USER_ID = os.getenv('QC_USER_ID')
API_TOKEN = os.getenv('QC_API_KEY')
BASE_URL = os.getenv('BASE_URL')
PROJECT_ID = os.getenv('PROJECT_ID')
ALGO_ID = os.getenv('ALGO_ID')


def get_headers():
    # Get timestamp
    timestamp = f'{int(time())}'
    time_stamped_token = f'{API_TOKEN}:{timestamp}'.encode('utf-8')

    # Get hashed API token
    hashed_token = sha256(time_stamped_token).hexdigest()
    authentication = f'{USER_ID}:{hashed_token}'.encode('utf-8')
    authentication = b64encode(authentication).decode('ascii')

    # Create headers dictionary.
    return {
        'Authorization': f'Basic {authentication}',
        'Timestamp': timestamp
    }


if __name__ == "__main__":
    # Authenticate to verify credentials
    response = post(f'{BASE_URL}/authenticate', headers=get_headers())
    print(response.json())
