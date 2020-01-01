# Project 2

Server side:
- List of rooms
- Participants in each room
- Messages in each room

Client Side:
- Username
- Current room
- Messages in current room

## User flows:
Below is the step by step description of the user flows and their client/server work split.

### Page Load |
1. Check localStorage if user has visited before (username, room)
1.1. If yes, load the last room he visited
1.2. If not, prompt for username, load 'general' room

### Create room | createRoom()
1. Check if room exists
2. Send room creation request to server
3. Server creates room and emits message to everyone with new room
4. Client adds new room to rooms list

### Join room | joinRoom()
1. Client sends request to server
2. Server checks if room exists, creates it if it does not
3. Server removes user from existing room, creates him in new room
4. Server sends room information (name, participants, messages)
5. Client runs changeRoom with received data
X. Updating participants list for all other participants

### changeRoom()
