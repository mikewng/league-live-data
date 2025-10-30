from config import LEAGUE_LIVE_API, BACKEND_API
import requests
import urllib3
from result import Result

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def league_live_api() -> Result:
    try:
        response = requests.get(LEAGUE_LIVE_API, verify=False)
        response.raise_for_status()

        data = response.json()

        # test print
        print(data['activePlayer']['currentGold'])

        return Result.success(data=data)
    except Exception as e:
        return Result.failure(error=f"Failed to fetch API: {str(e)}")
    
def establish_connection(username: str, token: str) -> Result:
    try:
        payload = {
            "username": username,
            "token": token
        }

        response = requests.post(
            "http://localhost:8000/api/connection/establish",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=10
        )

        response.raise_for_status()
        return Result.success(data=response.json())

    except Exception as e:
        return Result.failure(error=f"Failed to establish connection: {str(e)}")


def send_to_backend(data: dict, token: str) -> Result:
    try:
        payload = {
            "data": data
        }

        response = requests.post(
            BACKEND_API,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=10
        )

        response.raise_for_status()
        return Result.success(data=response.json())

    except Exception as e:
        return Result.failure(error=f"Failed to send data to backend: {str(e)}")


def disconnect_session(username: str, token: str) -> Result:
    try:
        payload = {
            "username": username,
            "token": token
        }

        response = requests.post(
            "http://localhost:8000/api/connection/disconnect",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=10
        )

        response.raise_for_status()
        return Result.success(data=response.json())

    except Exception as e:
        return Result.failure(error=f"Failed to disconnect: {str(e)}")