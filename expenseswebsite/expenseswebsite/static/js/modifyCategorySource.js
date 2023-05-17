const editCat = document.querySelector('#edit-category')
const saveCat = document.querySelector('#save-category')
saveCat.style.display = 'none'
const confirmDelCat = document.querySelector('#del-cat-confirm')
const categoryInput = confirmDelCat.parentElement.querySelector('#inputGroupSelect')

const catParent = categoryInput.parentElement
const editCatInput = document.createElement('input')
editCatInput.setAttribute('name', 'del-category')
editCatInput.classList.add('w-25')

const editSource = document.querySelector('#edit-source')
const saveSource = document.querySelector('#save-source')
saveSource.style.display = 'none'
const confirmDelSrc = document.querySelector('#del-src-confirm')
const sourceInput = confirmDelSrc.parentElement.querySelector('#inputGroupSelect')

const sourceParent = sourceInput.parentElement
const editSourceInput = document.createElement('input')
editSourceInput.setAttribute('name', 'del-source')
editSourceInput.classList.add('w-25')


editCat.addEventListener('click', () => {
    if (categoryInput.value !== "") {
        //note: with display none/block, user can inspect element and edit it as both are "accessbile" -- avoidable if creating of buttons in JS instead?
        editCat.style.display = 'none'
        saveCat.style.display = 'block'

        catParent.removeChild(categoryInput)
        catParent.prepend(editCatInput)
        editCatInput.focus()
        editCatInput.value = categoryInput.value
    }
})


saveCat.addEventListener('click', () => {
    //fetch to save changes
    fetch('/settings/edit-category', {
        body: JSON.stringify({
            'old': categoryInput.value,
            'new': editCatInput.value,
        }),
        //change this to put method? deal with CSRF token somehow
        method: "POST"
    })
    .then(() => {
        location.reload()
    })
})


categoryInput.addEventListener('change', (e) => {
    if (e.target.value !== null) {
        confirmDelCat.disabled = false
        editCat.disabled = false
        confirmDelCat.onclick = () => {
            return confirm('Are you sure you want to delete this category? This will delete all expenses under the selected category as well.')
        }
    }
})


editSource.addEventListener('click', () => {
    if (sourceInput.value !== "") {
        editSource.style.display = 'none'
        saveSource.style.display = 'block'

        sourceParent.removeChild(sourceInput)
        sourceParent.prepend(editSourceInput)
        editSourceInput.focus()
        editSourceInput.value = sourceInput.value
    }
})


saveSource.addEventListener('click', () => {
    //fetch to save changes
    fetch('/settings/edit-source', {
        body: JSON.stringify({
            'old': sourceInput.value,
            'new': editSourceInput.value,
        }),
        //change this to put method? deal with CSRF token somehow
        method: "POST"
    })
    .then(() => {
        location.reload()
    })
})


sourceInput.addEventListener('change', (e) => {
    if (e.target.value !== null) {
        confirmDelSrc.disabled = false
        editSource.disabled = false
        confirmDelSrc.onclick = () => {
            return confirm('Are you sure you want to delete this source? This will delete all income under the selected source as well.')
        }
    }
})


//event listener for key up -- escape -- revert inputs to select
document.addEventListener('keyup', (e) => {
    if (e.key === 'Escape') {
        try {
            catParent.removeChild(editCatInput)
            catParent.prepend(categoryInput)
            editCat.style.display = 'block'
            saveCat.style.display = 'none'

            sourceParent.removeChild(editSourceInput)
            sourceParent.prepend(sourceInput)
            editSource.style.display = 'block'
            editSource.style.display = 'none'
        } catch {
            
        }
    }
})