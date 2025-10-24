import requests
import time
import warnings

def get_current_gold():
    url = "https://127.0.0.1:2999/liveclientdata/allgamedata"
    for _ in range(5):
        warnings.simplefilter("ignore") #to suppress the warnings about insecure network request
        try:
            response = requests.get(url, verify=False)  # Ignore SSL certificate errors
            data = response.json()
            print(data['activePlayer']['currentGold'])
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except KeyError:
            print("Unable to retrieve current gold value from the response.")
        time.sleep(0.5)  # Wait for 0.5s second before the next iteration

# Call the function to run it
get_current_gold()