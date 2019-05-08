onPageLoad(
    () => {
        var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/socket');

        displayName = localStorage.getItem('displayName');

        if( ! displayName) {
            if( ! qs('#displayName') ) {
                document.location.replace('/login')
            }
        }
        if(qs('#submit_dp')) {
            qs('#submit_dp').onclick = () => {
                // ToDo: query if username exists on backend
                displayName = qs('#displayName').value;

                const request = new XMLHttpRequest();
                request.open('/username_exists')

                request.onload = () => {
                    const data = JSON.parse(request.responseText);
                    console.log(data);
                    if(data.success) {
                        if(data['username_exists']) {
                            alert("username exists")
                        } else {
                            localStorage.setItem('displayName', displayName);
                            document.location.replace('/')
                        }
                    }
                }

                const data = new FormData();
                data.append('dislayName', displayName);
                request.send(data);
            }
        }

        qs('#displayNameHead').innerText = displayName;
    }
);