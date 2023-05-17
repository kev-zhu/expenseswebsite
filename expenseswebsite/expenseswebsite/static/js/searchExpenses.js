const searchField = document.querySelector('#searchField')
const tableOutput = document.querySelector('.table-output')
const appTable = document.querySelector('.app-table')
const paginationContainer = document.querySelector('.pagination-container')
const tbody = document.querySelector('.table-body')
const noResult = document.querySelector('.no-result')

tableOutput.style.display = 'none'
noResult.style.display = 'none'

searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value

    if (searchValue.trim().length > 0) {
        fetch('/expenses/search-expenses', {
            body: JSON.stringify({ searchText: searchValue }),
            method: 'POST',
        })
        .then((res) => res.json())
        .then((data) => {            
            tableOutput.style.display = 'block'
            appTable.style.display = 'none'
            paginationContainer.style.display = 'none'

            tbody.innerHTML = ''
            if (data.length === 0) {
                noResult.style.display = 'block'
                tableOutput.style.display = 'none'
            }
            else {
                noResult.style.display = 'none'
                tableOutput.style.display = 'block'
                data.forEach(expense => {
                    tbody.innerHTML += `
                    <tr>
                        <td>${expense.amount.toFixed(2)}</td>
                        <td>${expense.category}</td>
                        <td>${expense.description}</td>
                        <td>${expense.date}</td>
                    </tr>`
                })
            }
        })
    }
    else {
        noResult.style.display = 'none'
        tableOutput.style.display = 'none'
        appTable.style.display = 'block'
        paginationContainer.style.display = 'block'
    }
})