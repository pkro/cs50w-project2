onPageLoad(
    () => {
        var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/socket');

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
            qs('#submit_dp').onclick = () => {
                
                displayName = qs('#displayName').value;

                const request = new XMLHttpRequest();
                request.open('POST', '/username_exists')

                request.onload = () => {
                    const data = JSON.parse(request.responseText);
                    console.log(data);
                    // THIS DOESN't WORK, data.username_exists is always true it seems
                    if(data.username_exists) {
                        alert("username exists")
                    } else {
                        localStorage.setItem('displayName', displayName);
                        document.location.replace('/')
                    }
                }

                const data = new FormData();
                data.append('displayName', displayName);
                request.send(data);
            }
        }
        // we are on the main page
        else {
            qs('#displayNameHead').innerText = displayName;

            qs('#logout').onclick = () => {
                const request = new XMLHttpRequest();
                request.open('POST', '/delete_user')

                request.onload = () => {
                    const data = JSON.parse(request.responseText);
                    console.log(data);
                    if(data.success) {
                        localStorage.removeItem('displayName')
                        document.location.replace('/login')
                    }
                }

                const data = new FormData();
                data.append('displayName', displayName);
                request.send(data);
            }
        }

    }
);