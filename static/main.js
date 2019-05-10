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

            // Enter should suffice to send "form"
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
            qs('#displayNameHead').innerText = displayName;

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
        
            var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
            currentRoom = localStorage.getItem('currentRoom');
            if( ! currentRoom ) {
                currentRoom = 'lobby'
            }

            socket.on('connect', () => {
                qs('#button_send').onclick = () => {
                        const message = qs('#userinput').value;
                        socket.emit('new message', {'message': message, 'room': currentRoom, 'displayName': displayName});
                    };
            });
            
            socket.emit('pull messages', {'room': currentRoom});

            socket.on('update messages', data => {
                data[currentRoom].forEach( message => {
                    // ToDo: Append messages to message view of current room
                    let message_li = document.createElement('li');
                    message_li.appendChild(document.createTextNode(`${message[0]} - ${message[1]}: ${message[2]}` ));
                    qs('#messages_list').appendChild(message_li)
                })
            });
        }

    }
);