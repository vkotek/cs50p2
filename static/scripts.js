// console.log('loading scripts.js');

document.addEventListener('DOMContentLoaded', () => {
      var room = localStorage.getItem('room');

      if (!room) {
        localStorage.setItem('room', 'general');
          room = localStorage.getItem('room');
      }

      joinRoom(room);
});

function load_page(room) {
    const request = new XMLHttpRequest();
    request.open('GET', `/rooms`);
    request.onload = () => {
        const response = JSON.parse(request.response);

        if ( !(room in response) ) {
          // If the room is not found, load 'General'
          console.log(`Room ${room} not found. Changing to General..`)
          room = 'general';
          localStorage.setItem('room', room)
        }

        // Update room name
        document.querySelector('title').innerHTML = `Chatr | ${room}`;
        document.querySelector('#room').innerHTML = room;

        // Load messages from room
        document.querySelector('#messages').innerHTML = '';
        const messages = Array(response[room].messages)[0];
        messages.forEach( window.show_message);

        // Load participants in room
        document.querySelector('#participants').innerHTML = '';
        const participants = Array(response[room].participants)[0];
        participants.forEach( window.show_participant);

        // Load list of all rooms
        document.querySelector('#rooms').innerHTML = '';
        const rooms = Object.keys(response);
        rooms.forEach( window.show_room);

    };
    request.send();
};

// HELPER FUNCTIONS

function updateParticipants(participants) {
  document.querySelector('#participants').innerHTML = '';
  var participants = Array(participants)[0];
  participants.forEach( window.show_participant );
}

function getRoom() {
  result = localStorage.getItem('room');
  if( !result ) {
      result = 'general'
      localStorage.setItem('room', result);
  }
  return result
};

function getUser() {
  result = localStorage.getItem('username');
  if(!result) {
    result = prompt("Enter your username:");
    localStorage.setItem('username', result);
  }
  return result
};

function joinRoom(name) {
  data = {
    'user': getUser(),
    'old_room': getRoom(),
    'new_room': name
  }

  socket.emit('join_room', data)
};

function show_message(msg, index) {

  const li = document.createElement('li');
  li.innerHTML = `<b title='Sent at ${msg.timestamp}'>${msg.user}</b>: ${msg.message}`;
  document.querySelector('#messages ').append(li);
  updateScroll();
}

function show_participant(p, index) {

  const li = document.createElement('li');
  li.innerHTML = `${p}`;
  document.querySelector('#participants ').append(li);
}

function show_room(room, index) {

  const li = document.createElement('li');
  const a = document.createElement('a');
  a.innerHTML = room;
  a.setAttribute('data-room', room)
  a.setAttribute('class', 'room')
  a.setAttribute('href', 'javascript: void(0)')
  a.setAttribute('onclick', `joinRoom('${room}')`)
  li.appendChild(a)
  document.querySelector('#rooms').append(li);
}

function updateScroll(){
  var element = document.getElementById("message_holder");
  element.scrollTop = element.scrollHeight;
}

// SOCKET FUNCTIONS

var socket = io();
socket.on('connect', () => {

  data = {
    'user': getUser(),
    'new_room':  'general',
  }

  // Client messages

  document.querySelector('#chat').onsubmit = () => {
    data = {
      'message': document.querySelector('#message').value,
      'user': getUser(),
      'room': getRoom()
    }
    document.querySelector('#message').value = "";
    socket.emit('message', data );
    return false
  }

  document.querySelector('#create-room').onsubmit = () => {
    room = document.querySelector('#create-room-name').value;
    socket.emit('socket_create_room', room);
    document.querySelector('#create-room-name').value = "";
    return false
  };

  // Server responses

  socket.on('new_message', msg => {
    console.log("RECEIVED: ", msg)
    if ( msg.room == getRoom() ) {
      show_message(msg);
      updateScroll();
    }
  });

  socket.on('created_room', room => {
    // When a room is created, add the room for everyone
    console.log('New room created: ', room)
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.innerHTML = room;
    a.setAttribute('data-room', room);
    a.setAttribute('class', 'room');
    a.setAttribute('href', 'javascript: void(0)');
    a.setAttribute('onclick', `joinRoom('${room}')`);
    li.appendChild(a);
    document.querySelector('#rooms').append(li);
  })

  socket.on('joined_room', room => {
    if( room.user == getUser() ) {
      // load joined room for the user who joined
      localStorage.setItem('room', room.name);
      window.load_page(room.name);
    } else if ( room.name == getRoom() ){
      // refresh for people in new room
      window.updateParticipants(room.participants);
    } else if ( room.old_room.name == getRoom() ) {
      // refresh participants for people in old room
      window.updateParticipants(room.old_room.participants);
    }
    console.log(`${room['user']} has joined ${room.name}.`)
  })
});
