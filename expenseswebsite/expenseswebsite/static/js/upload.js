const rows = document.querySelectorAll('.rows')
const postButton = document.querySelector('#post')

document.querySelectorAll('#type-choice').forEach( inp => {
    if (inp.value === "") {
        postButton.disabled = true
    }
})

// problem: everytime rowType is selected, this will create a new event listener
//      because of this, there can be many event listeners for one row type 
//      this becomes problematic because when choosing "add new type", this will run the newInput function for every event listener created
//      as a result this could create 2+ input for one type

//solution 1: add something where the program only makes one input and ignores the rest of the eventlisteners
//solution 2: add something where the program does not create any more event listeners if is already created once

//solution 2 is better because solution 1 could create an infinte amount of event listeners, and this would still need to run thorugh all of them and determine if it should proceed with new input?


const enableRowExpense = (rowChoice, expenseVisited) => {
    const noneSelected = rowChoice.querySelector('#none-selected')
    const categoryChoice = rowChoice.querySelector('#category-choice')
    const sourceChoice = rowChoice.querySelector('#source-choice')

    noneSelected.hidden = true
    categoryChoice.hidden = false
    sourceChoice.hidden = true
    categoryChoice.selectedIndex = 0
    sourceChoice.selectedIndex = 0

    if (!expenseVisited) {
    categoryChoice.addEventListener('change', () => {
            if (categoryChoice.value === "Create New Category") {
                try {
                    rowChoice.removeChild(categoryChoice)
                } catch {
                }
                    rowChoice.append(createNewInput(categoryChoice))
            }
        })
    }
}


const enableRowIncome = (rowChoice, incomeVisited) => {
    const noneSelected = rowChoice.querySelector('#none-selected')
    const categoryChoice = rowChoice.querySelector('#category-choice')
    const sourceChoice = rowChoice.querySelector('#source-choice')

    noneSelected.hidden = true
    categoryChoice.hidden = true
    sourceChoice.hidden = false
    categoryChoice.selectedIndex = 0
    sourceChoice.selectedIndex = 0

    if (!incomeVisited) {
        sourceChoice.addEventListener('change', () => {
            if (sourceChoice.value === "Create New Source") {
                try {
                    rowChoice.removeChild(sourceChoice)
                } catch {
                }
                rowChoice.append(createNewInput(sourceChoice))                
            }
        })
    }
}


rows.forEach(row => {
    const rowType = row.querySelector('.type')
    const rowChoice = row.querySelector('.choice')

    let expenseVisited = false
    let incomeVisited = false

    let rowTypeValue = rowType.querySelector('#type-choice').value     

    const displayRowChoice = (rowTypeValue, rowChoice) => {
        if (rowTypeValue === "expense") {
            rowChoice.querySelector('#none-selected').hidden = true
            rowChoice.querySelector('#category-choice').hidden = false
            enableRowExpense(rowChoice, expenseVisited)
            expenseVisited = true
        } else if (rowTypeValue === "income") {
            rowChoice.querySelector('#none-selected').hidden = true
            rowChoice.querySelector('#source-choice').hidden = false
            enableRowIncome(rowChoice, incomeVisited)
            incomeVisited = true
        }
    }

    displayRowChoice(rowTypeValue, rowChoice)
    
    rowType.addEventListener('change', () => { 
        rowTypeValue = rowType.querySelector('#type-choice').value     
        if (rowTypeValue === "expense") {
            enableRowExpense(rowChoice, expenseVisited)
            expenseVisited = true
        } else if (rowTypeValue === "income") {
            enableRowIncome(rowChoice, incomeVisited)
            incomeVisited = true
        }
    })
})


const createNewInput = (choiceType) => {
    const newInput = document.createElement('input')
    newInput.setAttribute('name', choiceType.name)
    newInput.setAttribute('id', choiceType.id)

    return newInput
}


postButton.onclick = () => {
    return confirm('Are you sure all of this data is correct? Please take another look before posting.')
}