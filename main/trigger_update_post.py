import requests
import json


def trigger_update_strategy(data):
    url = "http://127.0.0.1:9000/trigger_update"

    payload = json.dumps(data)
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
