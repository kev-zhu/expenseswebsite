let passwordField = null
let showPasswordToggle = null

const showPasswordToggles = document.querySelectorAll('.showPasswordToggle')


const handleToggleInput = (e) => {
    if (showPasswordToggle.textContent==='SHOW') {
        showPasswordToggle.textContent = 'HIDE'
        passwordField.setAttribute("type", "text")
    }
    else {
        showPasswordToggle.textContent = 'SHOW'
        passwordField.setAttribute("type", "password")
    }
}

showPasswordToggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
        //change passfield and showPassToggle Field to its children of the current clicks' parent
        passwordField = toggle.parentElement.querySelector('.passwordField')
        showPasswordToggle = toggle.parentElement.querySelector('.showPasswordToggle')

        handleToggleInput()
    })
})
