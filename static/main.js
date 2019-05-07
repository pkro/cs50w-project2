onPageLoad(
    () => {
        var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/socket');

        display_name = localStorage.getItem('display_name');

        if( ! display_name) {
            if( ! qs('#display_name') ) {
                document.location.replace('/login')
            }
        }
        if(qs('#submit_dp')) {
            qs('#submit_dp').onclick = () => {
                // ToDo: query if username exists on backend
                localStorage.setItem('display_name', qs('#display_name').value);
                document.location.replace('/')
            }
        }
    }
);