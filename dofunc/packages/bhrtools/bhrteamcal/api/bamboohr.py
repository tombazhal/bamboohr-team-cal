import requests
import json
from utils import dates

class BambooHR:
    def __init__(self, api_key, domain):
        self.api_base_url = f"https://api.bamboohr.com/api/gateway.php/{domain}"

        self.session = requests.Session()
        self.session.auth = (api_key, '')
        self.session.headers = {
            'Accept': 'application/json'
        }

    def get_whos_out(self, start_date, end_date):
        url = f"{self.api_base_url}/v1/time_off/whos_out/"
        params = {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception(f"Error getting whos out data: {response.status_code}")

    def get_custom_report(self, report_id):
        url = f"{self.api_base_url}/v1/reports/{report_id}?format=json"
        response = self.session.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception(f"Error getting custom report: {response.status_code}")

    def get_time_off_request(self, request_id, start_date, end_date):
        url = f"{self.api_base_url}/v1/time_off/requests/"
        params = {
            'id': request_id,
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception(f"Error getting time off request: {response.status_code}")

    def check_time_off_request(self, request_id, eligible_types):
        requests_from, requests_to = dates.get_requests_range()

        tmoff_requests = self.get_time_off_request(request_id, requests_from, requests_to)
        tmoff_request = tmoff_requests[0]

        if tmoff_request['status']['status'] != 'approved':
            return False

        if int(tmoff_request['type']['id']) not in eligible_types:
            return False

        return tmoff_request
