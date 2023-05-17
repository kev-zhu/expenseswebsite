const usernameField = document.querySelector('#usernameField')
const feedbackArea = document.querySelector('.invalid-feedback')
const emailField = document.querySelector("#emailField")
const emailFeedbackArea = document.querySelector('.email-feedback')
const submitBtn = document.querySelector('.submit-btn')

// if usr and email both incorrect -- then one of them is fixed, register btn enabled again -- fix async

//trycatch blocks used to deal with reusing of this js page -- for pages without username/email fields like in password reset



emailField.addEventListener('keyup', (e) => {
    const emailVal = e.target.value

    emailField.classList.remove('is-invalid')
    emailFeedbackArea.style.display = 'none'

    if (emailVal.length > 0) {
        fetch('/authentication/validate-email', {
            body: JSON.stringify({
                'email': emailVal
            }),
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            if (data.email_error) {
                submitBtn.disabled = true
                emailField.classList.add('is-invalid')
                emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`
                emailFeedbackArea.style.display = "block"
            } else {
                submitBtn.removeAttribute('disabled')
            }
        })
    }
})

usernameField.addEventListener('keyup', (e) => {
    const usernameVal = e.target.value

    usernameField.classList.remove('is-invalid')
    feedbackArea.style.display = "none"

    if (usernameVal.length > 0) {
        fetch('/authentication/validate-username', {
            body: JSON.stringify({
                'username': usernameVal
            }),
            method: "POST",
        })
        .then(res => res.json())
        .then(data => {
            if (data.username_error) {
                submitBtn.disabled = true
                usernameField.classList.add('is-invalid')
                feedbackArea.innerHTML = `<p>${data.username_error}</p>`
                feedbackArea.style.display = "block"
            } else {
                submitBtn.removeAttribute('disabled')
            }
        })
    }
})
