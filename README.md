# Introduction
This is a simple and goofy application that reads a person's live game data and passes into a better informed AI assistant that will guide you and also roast your gameplay progression. Connects player's live data on local port via a simple application that will constantly push the data every 2-5 seconds to the backend, in which does its core functionalities, including:
- Formatting Live Client Data
- Passing Changes in Live Client Data to OpenAI prompt through an authorized session
- Utilizing matchup MVC github repos to obtain matchup stat data
- Discord bot that uses TTS to relay ai text from backend via websockets

TO DO:
1. Add an onChange-Like function that detects changes in major live game data stats - DONE
2. Integrate OpenAI agents or just regular chat API service functionality that fires every time there is a change - DONE
3. Send output to discord bot via websocket
    - Implement TTS functionality for bot
4. Add op.gg MVC to check champion matchups for better context


# Running Instructions

## Front End (Development)
1. cd frontend
2. python -m venv venv -> venv\Scripts\activate
3. pip install -r requirements
4. run main.py (python -m main.py)

## Back End (Development)
1. python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Back End (Turn into .exe Application)
1. cd frontend
2. pip install pyinstaller
3. pyinstaller league_live_connector.spec

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
    
