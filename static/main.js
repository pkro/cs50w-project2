onPageLoad(
    () => {
        var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/socket');

        displayName = localStorage.getItem('displayName');

        if( ! displayName) {
            let login_div = ce('div');
            let login_text = ce('h1');
            login_text.innerHTML = 'Please select a display name'
            displayName_form = ce('input');
            login_div.appendChild(login_text);
            login_div.appendChild(displayName_form);
            //document.body.appendChild(login_div)
        }
    }
)