# Running Instructions

## Front End (Development)
1. cd frontend
2. python -m venv venv -> venv\Scripts\activate
3. pip install -r requirements
4. run main.py (python -m main.py)

# Application Flow Chart
<img width="1485" height="673" alt="image" src="https://github.com/user-attachments/assets/bd09e891-8caf-4339-9a0f-6e066e282da1" />

## Frontend Structure
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
  

## Backend Structure
/app
- core
    - configs, dependencies, redis, database (eventually), etc.
- routers
    - ingest.py
        - in-memory storage
        - api/connection/establish
        - api/ingest
        - api/connection/disconnect
- schemas
    - auth.py
        - Connection request models
    - game_data.py
        - Game data in-memory storage object
    - player_data.py
        - Player data in-memory storage object
    - session.py
        - Session data in-memory storage object
- services
    - openai_service.py
        - Agent API calls, writing messages
    
