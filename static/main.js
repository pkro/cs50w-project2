onPageLoad(
    () => {
        // Check if user already has a displayName
        displayName = localStorage.getItem('displayName');
        if( ! displayName) {
            if( ! qs('#displayName') ) {
                document.location.replace('/login')
            }
        }

        // Are we on the login page? If yes, allow user to choose display name
        // and redirect to chat page
        if(qs('#submit_dp')) {
            var input = document.getElementById("myInput");
            // Enter should suffice to send login name
            var input = qs("#displayName");
            input.addEventListener("keyup", function(event) {
                // Number 13 is the "Enter" key on the keyboard
                if (event.keyCode === 13) {
                    event.preventDefault();
                    qs("#submit_dp").click();
            }
            });

            qs('#submit_dp').onclick = () => {
                displayName = qs('#displayName').value;

                const request = new XMLHttpRequest();
                request.open('POST', '/displayName_exists')

                request.onload = () => {
                    const data = JSON.parse(request.responseText);
                    if(data.displayName_exists) {
                        qs('.alert').style.display = "block";
                        qs('.alert').innerText =  "Display name already exists"
                    } else {
                        localStorage.setItem('displayName', displayName);
                        document.location.replace('/')
                    }
                }

                const data = new FormData();
                data.append('displayName', displayName);
                data.append('room', 'Lobby');
                request.send(data);
            }
        }

        // we are on the main page
        else {
            const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
            socket.on('connect', () => {
                
                /********************************************************************
                * Init - pull existing messages and rooms
                *********************************************************************/
                qs('#displayNameHead').innerText = displayName;
                currentRoom = localStorage.getItem('currentRoom');
                if( ! currentRoom ) {
                    currentRoom = 'Lobby'
                }
                socket.emit('pull rooms');
                socket.emit('pull messages', {'room': currentRoom});
                
                /********************************************************************
                * Event listeners for user controls
                *********************************************************************/
                qs('#button_send').onclick = () => {
                    const message = qs('#userinput').value;
                    socket.emit('new message', {'message': message, 'room': currentRoom, 'displayName': displayName});
                };
                
                // logout user
                qs('#logout').onclick = () => {
                    const request = new XMLHttpRequest();
                    request.open('POST', '/delete_displayName')

                    request.onload = () => {
                        const data = JSON.parse(request.responseText);
                        if(data.success) {
                            localStorage.removeItem('displayName')
                            document.location.replace('/login')
                        }
                    }

                    const data = new FormData();
                    data.append('displayName', displayName);
                    request.send(data);
                }
                
                // Create new room by typing in new name
                // ToDo: Check if room exists + message
                // ToDo: put user in newly created room
                var create_room = qs("#create_room");
                create_room.addEventListener("keyup", function(event) {
                    if (event.keyCode === 13) {
                        event.preventDefault();
                        const request = new XMLHttpRequest();
                        request.open('POST', '/create_room')
                        const data = new FormData();
                        data.append('new_room', create_room.value);
                        currentRoom = create_room.value;
                        create_room.value = "";
                        request.send(data);
                    }
                });

                /********************************************************************
                * Socket listeners
                *********************************************************************/                
                socket.on('update rooms', data => {
                    qs('#room_list').innerHTML = "";
                    data.forEach( room => {
                        let room_li = document.createElement('li');
                        room_li.setAttribute('class', 'room_listitem')
                        room_li.appendChild(document.createTextNode(`${room}` ));
                        qs('#room_list').appendChild(room_li)
                    })
                });
                
                socket.on('update messages', data => {
                    qs('#messages_list').innerHTML = "";
                    data.forEach( message => {
                        let message_li = document.createElement('li');
                        message_li.appendChild(document.createTextNode(`${message[0]} - ${message[1]}: ${message[2]}` ));
                        qs('#messages_list').appendChild(message_li)
                    })
                });
            });
        }

    }
);