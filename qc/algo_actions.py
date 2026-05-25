from . import quantconnect as qc
from requests import post
import json
import os
from dotenv import load_dotenv

load_dotenv()

class LiveUpdate():
    def __init__(self):
        self.deploy_id = os.getenv('DEPLOY_ID')
        self.project_id = os.getenv("PROJECT_ID")
        self.base_url = os.getenv('BASE_URL')
        self.node_id = None

        self.brokerage_id = os.getenv('INERACTIVE_BROKERS_BROKERAGE_ID')
        self.ib_username = os.getenv('IBKR_USER_NAME')
        self.ib_account = os.getenv('IB_ACC_ID')
        self.ib_password = os.getenv('IB_PASSWORD')

    def read_stats(self) -> str:
        payload = {
            "projectId": self.project_id,
            "deployId": self.deploy_id
        }

        response = post(f'{self.base_url}/live/read',
                        headers=qc.get_headers(), json=payload)

        result = response.json()
        # print(result)
        # if result['success']:
        #     print("Live Algorithm Statistics:")
        #     print(result)

        return result

    def start_live_algo(self):
        def get_compile_id() -> str:
            payload = {
                "projectId": self.project_id
            }

            response = post(f"{self.base_url}/compile/create",
                            headers=qc.get_headers(), json=payload)

            result = response.json()
            compileId = result['compileId']

            return compileId

        self.compile_id = get_compile_id()

        def node_id() -> str:  # Get live node ID
            payload = {
                "projectId": self.project_id
            }

            response = post(f'{self.base_url}/projects/nodes/read',
                            headers=qc.get_headers(), json=payload)

            result = response.json()
            node = result['nodes']['live'][0]['id']

            return node

        node = node_id()

        payload = {
            "versionId": -1,
            "projectId": self.project_id,
            "compileId": self.compile_id,
            "nodeId": node,
            'brokerage': {
                "id": self.brokerage_id,
                "user": self.ib_username,
                'password': self.ib_password,
                'environment': os.getenv('ENVIRONMENT'),
                'account': self.ib_account
            },
            'dataProviders': {
                'QuantConnectBrokerage': {
                    'id': 'QuantConnectBrokerage'
                },
                "INTERACTIVE_BROKERS_BROKERAGE": {
                    'id': self.brokerage_id,
                    'id-user-name': self.ib_username,
                    'ib-account': self.ib_account,
                    'ib-password': self.ib_password,
                    'ib-weekly-restart-utc-time': '10:00:00',
                }
            }
        }

        response = post(f"{qc.BASE_URL}/live/create",
                        headers=qc.get_headers(), json=payload)

        result = response.json()
        deploy_id = result['deployId']

        # Check if the request was successful and print the result
        if result['success']:
            print("Live Algorithm Created Successfully:")
            print(result)

    def stop_live_algo(self):
        payload = {
            'projectId': self.project_id
        }

        response = post(f"{self.base_url}/live/update/stop",
                        headers=qc.get_headers(), json=payload)
        result = response.json()
        
        return result

    def liquidate(self):
        payload = {
            'projecId': self.project_id
        }

        response = post(f"{self.base_url}", headers=qc.get_headers(), json=payload)
        result = response.json()
        # print(json.dump(result, indent=2))

        return result


if __name__ == "__main__":
    actions = LiveUpdate()
    print(json.dumps(actions.read_stats(), indent=2))
