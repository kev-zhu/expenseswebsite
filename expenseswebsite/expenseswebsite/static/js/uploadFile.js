const uploadButton = document.querySelector('#choose-file')
const continueButton = document.querySelector('#continue')

uploadButton.onclick = (event) => {
    event.preventDefault()
    //fetch something that checks for file existance
    //then if exist ==> pop up warning 
    fetch('/upload/user-has-file')
    .then(res => res.json())
    .then(file_exists => {
        //prevention of reload with preventDefault --> resolve with JS form submit()
        const formField = uploadButton.parentElement
        if (file_exists.result) {
            const askConfirm = confirm('Are you sure you want to upload a new file? This would replace the previously uploaded file.')
            if (askConfirm) {
                formField.submit()
            } 
        } else {
            formField.submit()
        }
    })
}

continueButton.addEventListener('click', () => {
    pathArr = window.location.pathname.split('/')
    pathArr.pop()
    pathArr.push('upload-changes')
    uploadPath = pathArr.join('/')
    window.location.href = window.location.origin + uploadPath
})

document.addEventListener('DOMContentLoaded', () => {
    fetch('/upload/user-has-file')
    .then(res => res.json())
    .then(file_exists => {
        if (!file_exists.result) {
            continueButton.disabled = true
        }
    })
})
