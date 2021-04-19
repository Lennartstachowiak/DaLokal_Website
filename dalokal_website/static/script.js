function flashMessage() {
    if (flash_message == "email") {
        document.getElementById('errorMessage').innerHTML = 'Email address already exists. Go to <a href="/login">login page</a>'
    } if (flash_message == "psw") {
        document.getElementById('errorMessage').innerHTML = 'The passwords don\'t match.'
    } if (flash_message == "") {
        document.getElementById('errorMessage').innerHTML = ''
    } if (flash_message == "wrong") {
        document.getElementById('errorMessage').innerHTML = 'Your entered email or password is not correct'
    }
}