function flashMessage(flash_message) {
    if (flash_message == "") {
        document.getElementById('errorMessage').style.display = 'none'
    } if (flash_message == "email") {
        document.getElementById('errorMessage').style.display = 'flex'
        document.getElementById('errorMessage').innerHTML = '<a href="/login">Email address already exists. Go to <br><span class="underline">login page</span></a>'
    } if (flash_message == "emailEdit") {
        document.getElementById('errorMessage').style.display = 'flex'
        document.getElementById('errorMessage').innerHTML = 'Email address already exists.'
    } if (flash_message == "psw") {
        document.getElementById('errorMessage').style.display = 'flex'
        document.getElementById('errorMessage').innerHTML = 'The passwords don\'t match.'
    } if (flash_message == "wrong") {
        document.getElementById('errorMessage').style.display = 'flex'
        document.getElementById('errorMessage').innerHTML = 'Your email or password is not correct!'
    } if (flash_message == "name") {
        document.getElementById('errorMessage').style.display = 'flex'
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

function adressChange() {
    if (document.getElementById('farmStreet').value != "" ||
    document.getElementById('farmPostalCode').value != "" ||
    document.getElementById('farmCity').value != "") {
        document.getElementById('farmStreet').required = true;
        document.getElementById('farmPostalCode').required = true;
        document.getElementById('farmCity').required = true;
    } else {
        document.getElementById('farmStreet').required = false;
        document.getElementById('farmPostalCode').required = false;
        document.getElementById('farmCity').required = false;
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

function filter(filter) {
    farmBox = document.getElementById('farmBoxesContainer')
    farm = farmBox.getElementsByTagName('section')

    for (x = 0; x < farm.length; x++) {
        if (filter === 'all') {
            farm[x].style.display = '';
        }
        else {
            categories = farm[x].getElementsByTagName('p');
            if (categories[0] == undefined) {
                farm[x].style.display = 'none';
            }
            else {
                var count = 0
                for (y = 0; y < categories.length; y++) {
                    category = categories[y].innerHTML
                    if (category === filter) {
                        count++
                    }
                }
                if (count === 0) {
                    farm[x].style.display = 'none';
                }
                else {
                    farm[x].style.display = '';
                }
            }
        }
    }
}

function checkIfUser(notMyAccount) {
    if (notMyAccount == 1) {
        document.getElementById('edit').style.display = 'none';
        document.getElementById('addProduct').style.display = 'none';
    }
}

function edit(input) {
    if (input == 1) {
        document.getElementById('edit').style.display = 'none';
    }
}