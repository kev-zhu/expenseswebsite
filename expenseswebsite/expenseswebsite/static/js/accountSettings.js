const conf_deactivate = document.querySelector('#confirm-deactivate')
const conf_delete = document.querySelector('#confirm-delete')


const edit_info = document.querySelector("#edit-account-info")
const save_info = document.querySelector("#save-account-info")
save_info.style.display = "none"

const username = document.querySelector("#username")
const name = document.querySelector("#name")

const changeUsername = document.createElement('input')
changeUsername.type = 'text'
changeUsername.value = username.innerHTML
changeUsername.placeholder = 'New Username'
changeUsername.classList.add('w-25')
changeUsername.classList.add('form-control')

const changeName = document.createElement('input')
changeName.type = 'text'
changeName.value = name.innerHTML === "No name on record" ? "" : name.innerHTML
changeName.placeholder = 'New Name'
changeName.classList.add('w-25')
changeName.classList.add('form-control')

userParent = username.parentElement
nameParent = name.parentElement


conf_deactivate.onclick = () => {
    return confirm('Are you sure you want to deactivate your account? Please read the information below the deactivation button before confirming.')
}
conf_delete.onclick = () => {
    return confirm('Are you sure you want to delete your account? Please read the information below the delete button before confirming')
}

edit_info.addEventListener("click", () => {
    userParent.removeChild(username)
    userParent.appendChild(changeUsername)
    
    nameParent.removeChild(name)
    nameParent.appendChild(changeName)

    edit_info.style.display = "none"
    save_info.style.display = "block"
})

save_info.addEventListener("click", () => {
    edit_info.style.display = "block"
    save_info.style.display = "none"

    username.innerHTML = changeUsername.value
    name.innerHTML = changeName.value

    userParent.removeChild(userParent.lastChild)
    userParent.append(username)
    nameParent.removeChild(nameParent.lastChild)
    nameParent.append(name)

    //fetching here to update it 
    fetch('/settings/change-account-info', {
        body: JSON.stringify({
            'username': changeUsername.value,
            'name': changeName.value
        }),
        method: "POST"
    })
})

//also add an event listener for change to check up on username valid
//let curr username bypass
changeUsername.addEventListener('keyup', (e) => {
    const usernameVal = e.target.value
    changeUsername.classList.remove('is-invalid')

    fetch('/authentication/validate-username', {
        body: JSON.stringify({
            'username': usernameVal
        }),
        method: "POST",
    })
    .then(res => res.json())
    .then(data => {
        if (data.username_error && usernameVal !== username.innerHTML) {
            save_info.disabled = true
            changeUsername.classList.add('is-invalid')
        } else {
            save_info.removeAttribute('disabled')
        }
    })
})