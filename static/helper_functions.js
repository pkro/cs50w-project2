function qs(selector) {
    return document.querySelector(selector);
}

function qsa(selector) {
    return document.querySelectorAll(selector);
}

function onPageLoad(func) {
    document.addEventListener('DOMContentLoaded', func);
}

function ce(tag) {
    return document.createElement(tag);
}

function cl(text) {
    console.log(text);
}

function update_rooms() {
    const request = new XMLHttpRequest();
    request.onload = () => {
        const rooms = JSON.parse(request.responseText);
        if (rooms) {
            qs('#room_list').innerHTML = "";
            rooms.forEach(room => {
                let room_li = document.createElement('li');
                room_li.setAttribute('class', 'room_listitem');
                // I don't need to use a dataset but may be useful later
                room_li.setAttribute('data-room_name', room);
                room_li.onclick = () => {
                    localStorage.setItem('room', room_li.dataset.room_name)
                    const subrequest = new XMLHttpRequest();
                    subrequest.open('POST', '/create_room')
                    const data = new FormData();
                    data.append('room', room_li.dataset.room_name);
                    subrequest.send(data);
                }
                if (room == localStorage.getItem('room')) {
                    room_li.setAttribute('class', 'selected');
                }
                room_li.appendChild(document.createTextNode(`${room}`));
                qs('#room_list').appendChild(room_li);
            });
        }
    }
    request.open('GET', '/pull_rooms');
    request.send();
}

function update_messages(room) {
    const request = new XMLHttpRequest();
    request.onload = () => {
        const messages = JSON.parse(request.responseText);
        qs('#messages_list').innerHTML = "";
        messages.forEach(message => {
            let message_li = document.createElement('li');
            message_li.appendChild(document.createTextNode(`${message[0]} - ${message[1]}: ${message[2]}`));
            qs('#messages_list').appendChild(message_li)
        });
    }

    request.open('GET', '/pull_messages');
    request.send();
}

function update_users() {
    const request = new XMLHttpRequest();
    request.onload = () => {
        qs('#users_list').innerHTML = "";
        const data = JSON.parse(request.responseText);
        data.forEach(user => {
            let user_li = document.createElement('li');
            user_li.appendChild(document.createTextNode(`${user}`));
            qs('#users_list').appendChild(user_li)
            if (user == localStorage.getItem('user')) {
                user_li.setAttribute('class', 'selected');
            }
        });
    }

    request.open('GET', '/pull_users');
    request.send();
}

function send_message(message) {
    const request = new XMLHttpRequest();
    request.open('POST', '/send_message');
    const data = new FormData();
    data.append('message', message);
    request.send(data);
}