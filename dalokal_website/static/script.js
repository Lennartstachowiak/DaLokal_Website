function flashMessage() {
    if (flash_message == "email") {
        document.getElementById('errorMessage').innerHTML = '<a href="/login">Email address already exists. Go to <br><span class="underline">login page</span></a>'
    } if (flash_message == "psw") {
        document.getElementById('errorMessage').innerHTML = 'The passwords don\'t match.'
    } if (flash_message == "") {
        document.getElementById('errorMessage').innerHTML = ''
    } if (flash_message == "wrong") {
        document.getElementById('errorMessage').innerHTML = 'Your email or password is not correct!'
    } if (flash_message == "name") {
        document.getElementById('errorMessage').innerHTML = 'Farm name already taken! Please take other name'
    }
}

function timecheck(b, e) {
    if (document.getElementById(b).value != '') {
        document.getElementById(e).required = true;
    } else {
        document.getElementById(e).required = false;
    } if (document.getElementById(e).value != '') {
        document.getElementById(b).required = true;
    } else {
        document.getElementById(b).required = false;
    }
}
function clearTimeInput(b, e) {
    document.getElementById(b).value = ''
    document.getElementById(e).value = ''
}


function openModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = 'block'
}

function closeModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = 'none'
}

