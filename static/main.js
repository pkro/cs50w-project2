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
            // otherwise room is not found and mayhem
            socket.on('disconnect', function () {
                socket.emit('disconnected');
                localStorage.removeItem('currentRoom')
            });

            socket.on('connect', () => {
                /********************************************************************
                * Event listeners for user controls
                *********************************************************************/
                qs('#button_send').onclick = () => {
                    const message = qs('#userinput').value;
                    qs('#userinput').value = '';
                    socket.emit('new message', {'message': message, 'room': currentRoom, 'displayName': displayName});
                }
                // ctrl+enter sends input (ctrl is necessary because field is multiline)
                qs('#userinput').addEventListener("keyup", event => {
                    if(event.ctrlKey && event.keyCode == 13) {
                        qs('#button_send').click();
                    }
                });
                // logout user
                qs('#logout').onclick = () => {
                    const request = new XMLHttpRequest();
                    request.open('POST', '/delete_displayName')

                    request.onload = () => {
                        const data = JSON.parse(request.responseText);
                        if(data.success) {
                            localStorage.removeItem('displayName')
                            localStorage.removeItem('currentRoom')
                            document.location.replace('/login')
                        }
                    }

                    const data = new FormData();
                    data.append('displayName', displayName);
                    data.append('room', currentRoom);
                    request.send(data);
                }
                
                // Create new room by typing in new name + enter
                var create_room = qs("#create_room");
                create_room.addEventListener("keyup", function(event) {
                    if (event.keyCode === 13) {
                        event.preventDefault();
                        const request = new XMLHttpRequest();
                        request.open('POST', '/create_room')
                        const data = new FormData();
                        data.append('new_room', create_room.value);
                        data.append('displayName', displayName);
                        currentRoom = create_room.value;
                        localStorage.setItem('currentRoom', currentRoom);
                        create_room.value = "";
                        request.send(data);
                    }
                });

                qsa('.room_listitem').forEach ( room_li => {

                });

                /********************************************************************
                * Socket listeners
                *********************************************************************/                
                socket.on('update rooms', data => {
                    qs('#room_list').innerHTML = "";
                    data.forEach( room => {
                        let room_li = document.createElement('li');
                        room_li.setAttribute('class', 'room_listitem');
                        // I don't need to use a dataset but may be useful later
                        room_li.setAttribute('data-room_name', room);
                        room_li.onclick = () => {
                            const request = new XMLHttpRequest();
                            request.open('POST', '/change_room')
                            const data = new FormData();
                            data.append('new_room', room_li.dataset.room_name);
                            data.append('displayName', displayName);
                            currentRoom = room_li.dataset.room_name;
                            localStorage.setItem('currentRoom', currentRoom);
                            request.send(data);
                        }
                        room_li.appendChild(document.createTextNode(`${room}` ));
                        qs('#room_list').appendChild(room_li);
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

                socket.on('update users', data => {
                    qs('#users_list').innerHTML = "";
                    cl(data)
                    data.forEach( user => {
                        let user_li = document.createElement('li');
                        user_li.appendChild(document.createTextNode(`${user}`));
                        qs('#users_list').appendChild(user_li)
                    })
                });
                
                /********************************************************************
                * Init - pull existing messages and rooms
                *********************************************************************/
                qs('#displayNameHead').innerText = displayName;
                currentRoom = localStorage.getItem('currentRoom');
                if( ! currentRoom ) {
                    currentRoom = 'Lobby'
                }
                socket.emit('pull rooms', {'displayName': displayName, 'room': currentRoom});
                // we take care of that in pull rooms event as well
                // socket.emit('pull users', {'room': currentRoom});
                socket.emit('pull messages', {'room': currentRoom});
                
            });
        }

    }
);