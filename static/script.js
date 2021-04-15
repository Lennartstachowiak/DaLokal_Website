function flashMessage() {
    if (flash_message == "email") {
        document.getElementById('errorEmail').innerHTML = 'Email address alredy exists. Go to <a href="/log-in">login page</a>'
    } if (flash_message == "psw") {
        document.getElementById('errorEmail').innerHTML = 'The passwords don\'t match.'
    } if (flash_message == "") {
        document.getElementById('errorEmail').innerHTML = ''
    }
}