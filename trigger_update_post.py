import requests
import json


def trigger_update_strategy(data):
    url = "http://13.237.171.252:9000/trigger_update"  #13.237.171.252

    payload = json.dumps(data)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
