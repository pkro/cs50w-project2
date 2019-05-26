onPageLoad( () => {

/********************************************************************
 * Init - pull existing messages and rooms
 *********************************************************************/
const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

var user = localStorage.getItem("user");
var room = localStorage.getItem('room');

qs('#userHead').innerText = user;

update_rooms();
update_messages();
update_users();

/********************************************************************
* Event listeners for user controls
*********************************************************************/
qs('#button_send').onclick = () => {
    send_message(qs('#userinput').value);
    qs('#userinput').value = '';
}

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
    request.open('GET', '/logout')

    request.onload = () => {
        const data = JSON.parse(request.responseText);
        if (data.success) {
            localStorage.removeItem('user')
            localStorage.removeItem('room')
            document.location.replace('/')
        }
    }
    request.send();
}

// Create new room by typing in new name + enter
var create_room = qs("#create_room");
create_room.addEventListener("keyup", function (event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        const request = new XMLHttpRequest();
        request.open('POST', '/create_room')
        const data = new FormData();
        data.append('room', create_room.value);
        room = create_room.value;
        localStorage.setItem('room', room);
        create_room.value = "";
        request.send(data);
    }
});

/********************************************************************
* Socket listeners
*********************************************************************/
socket.on('update rooms', () => {
    update_rooms();
});

socket.on('update messages', () => {
    update_messages();
});

socket.on('update users', () => {
    update_users();
});

}); // onpageload