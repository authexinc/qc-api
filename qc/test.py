from requests import post, get
# import qc.quantconnect as qc
import quantconnect as qc
import json
import algo_actions as aa
from dotenv import load_dotenv
import os

load_dotenv()

def order_log():
    payload = {
        'algorithmId': os.getenv('ALGO_ID'),
        'start':0,
        'end':1,
        'projectId':os.getenv('PROJECT_ID')
    }
    
    response = post(f'')