const selectInput = document.querySelector('.income-selected')
const selectedParent = selectInput.parentElement

//this is to let user revert back to their prev if they choose to 'esc' from creating new expense
let prevOption = selectInput.selectedIndex

const textInput = document.createElement('input')
textInput.type = 'text'
textInput.className = 'form-control form-control-sm'
textInput.name = 'source'
textInput.placeholder = 'Input a New Source'

selectInput.addEventListener("change", () => {
    if (selectInput.value === 'Add a new option') {
        selectedParent.removeChild(selectInput)
        selectedParent.appendChild(textInput)
        textInput.value = ""
        textInput.focus()
    }
    else {
        prevOption = selectInput.selectedIndex
    }
})

//first escape doesnt work/register with event listener... fix?
//note: it seems like autofocus on the input box fixed this problem
textInput.addEventListener("keydown", (e) => {
    if (e.key === 'Escape') {
        selectedParent.removeChild(textInput)
        selectedParent.appendChild(selectInput)
        selectInput.selectedIndex = prevOption
    }
})