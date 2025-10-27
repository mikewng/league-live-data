# Running Instructions

## Front End (Development)
1. cd frontend
2. python -m venv venv -> venv\Scripts\activate
3. pip install -r requirements
4. run main.py (python -m main.py)


## Front End Structure
UI Components
1. Title
2. Notifications
    - Any logs that can help both user and dev keep track of app status
3. Secret Token Text Area
    - The API Token needed to access the Backend API Connection
4. Connect Button
    - Attempts to establish a connection (aka, is anyone else using this right now?)
    - If success, then give okay and validate connection
    - ** Currently, just a dummy call
5. Start Stream/Stop Stream
    - Constantly fire Live-Game API hit every 2-5s and send to the backend
    - **Eventually should be changed to only send the deltas, not the entire JSON