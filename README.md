# Project 2

Server side:
- List of rooms
- Participants in each room
- Last 100 messages in each room

Client Side:
- Username
- Current room
- Messages in current room

Summary:
- When user first enters the website, a username is requested.
- The default room is 'general' where the user will be redirected.

- Participants of all rooms are visible to everyone in the room.  

### /application.py
Main application file containing all the python code.

It is split into Flask Routes, Socket Handlers, and Helper functions.

#### Flask Routes
There are two routes, the homepage "/" and the API "/rooms" used to retrieve information all chatrooms.

### /templates/{layout.html,room.html}
Template files containing all HTML code.

### /static/scripts.js
All Javascript code is stored externally in this file.

### /static/style.css
Styling shee  ts for the page.
