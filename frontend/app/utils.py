from config import LEAGUE_LIVE_API, BACKEND_API
import requests

def league_live_api():
    try:
        response = requests.get("https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False, timeout=0.5)
        if response.status_code == 200:
            print(response.json())
    except Exception as e:
        print("Failed API")
        return