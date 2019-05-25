onPageLoad(
    () => {
        // If we're here, the user in localstorage doesn't exist 
        // or is not in sync with the flask session, so we better delete any leftovers
        user = localStorage.removeItem('user')

        var input = document.getElementById("myInput");

        // Enter should suffice to send login name
        // NOT keyup, otherwise enter triggers form submit before keyup happens
        var input = qs("#user");
        input.addEventListener("keydown", function (event) {
            // Number 13 is the "Enter" key on the keyboard
            if (event.keyCode === 13) {
                event.preventDefault();
                qs("#submit_dp").click();
            }
        });

        qs('#submit_dp').onclick = () => {
            user = qs('#user').value;

            const request = new XMLHttpRequest();
            request.open('POST', '/user_exists')

            request.onload = () => {
                const data = JSON.parse(request.responseText);
                if (data.user_exists) {
                    qs('.alert').style.display = "block";
                    qs('.alert').innerText = "Display name already exists"
                } else {
                    localStorage.setItem('user', user);
                    cl('x'+localStorage.getItem('user'));
                    document.loginform.submit();
                }
            }

            const data = new FormData();
            data.append('user', user);
            data.append('room', 'Lobby');
            request.send(data);
        }
    });