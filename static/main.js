onPageLoad(
    () => {

        const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
        /********************************************************************
       * Init - pull existing messages and rooms
       *********************************************************************/
        var user = localStorage.getItem("user");
        var currentRoom = localStorage.getItem('currentRoom');

        qs('#userHead').innerText = user;
        
        if (!currentRoom) {
            currentRoom = 'Lobby'
            localStorage.setItem('currentRoom', currentRoom)
        }

        socket.emit('pull rooms', { 'user': user, 'room': currentRoom });
        socket.emit('pull messages', { 'room': currentRoom });



        /********************************************************************
        * Event listeners for user controls
        *********************************************************************/
        qs('#button_send').onclick = () => {
            const message = qs('#userinput').value;
            qs('#userinput').value = '';
            socket.emit('new message', { 'message': message, 'room': currentRoom, 'user': user });
        }
        // ctrl+enter sends input (ctrl is necessary because field is multiline)
        qs('#userinput').addEventListener("keyup", event => {
            if (event.ctrlKey && event.keyCode == 13) {
                qs('#button_send').click();
            }
        });

        qs('#button_translate').onclick = () => {
            const message = qs('#userinput').value;
            const request = new XMLHttpRequest();
            request.onload = () => {
                const data = JSON.parse(request.responseText);
                if (data.translation) {
                    qs('#userinput').value = data.translation;
                }
            }
            request.open('POST', '/translate');
            const data = new FormData();
            data.append('message', message);
            request.send(data);
        };

        // logout user
        qs('#logout').onclick = () => {
            const request = new XMLHttpRequest();
            request.open('POST', '/delete_user')

            request.onload = () => {
                const data = JSON.parse(request.responseText);
                if (data.success) {
                    localStorage.removeItem('user')
                    localStorage.removeItem('currentRoom')
                    document.location.replace('/')
                }
            }

            const data = new FormData();
            data.append('user', user);
            data.append('room', currentRoom);
            request.send(data);
        }

        // Create new room by typing in new name + enter
        var create_room = qs("#create_room");
        create_room.addEventListener("keyup", function (event) {
            if (event.keyCode === 13) {
                event.preventDefault();
                const request = new XMLHttpRequest();
                request.open('POST', '/create_room')
                const data = new FormData();
                data.append('new_room', create_room.value);
                data.append('user', user);
                currentRoom = create_room.value;
                localStorage.setItem('currentRoom', currentRoom);
                create_room.value = "";
                request.send(data);
            }
        });

        /********************************************************************
        * Socket listeners
        *********************************************************************/
        socket.on('update rooms', data => {
            qs('#room_list').innerHTML = "";
            data.forEach(room => {
                let room_li = document.createElement('li');
                room_li.setAttribute('class', 'room_listitem');
                // I don't need to use a dataset but may be useful later
                room_li.setAttribute('data-room_name', room);
                room_li.onclick = () => {
                    const request = new XMLHttpRequest();
                    request.open('POST', '/change_room')
                    const data = new FormData();
                    data.append('new_room', room_li.dataset.room_name);
                    data.append('user', user);
                    request.send(data);
                }
                let suffix = ''
                if (room == localStorage.getItem('currentRoom')) {
                    suffix = ' *'
                }
                room_li.appendChild(document.createTextNode(`${room}${suffix}`));
                qs('#room_list').appendChild(room_li);
            })
        });

        socket.on('update messages', data => {
            qs('#messages_list').innerHTML = "";
            currentRoom = localStorage.getItem('currentRoom');
            if (data.room == currentRoom) {
                data.messages.forEach(message => {
                    let message_li = document.createElement('li');
                    message_li.appendChild(document.createTextNode(`${message[0]} - ${message[1]}: ${message[2]}`));
                    qs('#messages_list').appendChild(message_li)
                });
            }
        });

        socket.on('update users', data => {
            qs('#users_list').innerHTML = "";
            data.forEach(user => {
                let user_li = document.createElement('li');
                user_li.appendChild(document.createTextNode(`${user}`));
                qs('#users_list').appendChild(user_li)
            })
        });
    });