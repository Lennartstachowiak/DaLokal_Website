function flashMessage() {
    if (flash_message == "email") {
        document.getElementById('errorMessage').innerHTML = '<a href="/login">Email address already exists. Go to <br><span class="underline">login page</span></a>'
    } if (flash_message == "psw") {
        document.getElementById('errorMessage').innerHTML = 'The passwords don\'t match.'
    } if (flash_message == "") {
        document.getElementById('errorMessage').innerHTML = ''
    } if (flash_message == "wrong") {
        document.getElementById('errorMessage').innerHTML = 'Your email or password is not correct!'
    }
}