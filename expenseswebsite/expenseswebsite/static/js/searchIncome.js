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
        fetch('/income/search-income', {
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
                data.forEach(income => {
                    tbody.innerHTML += `
                    <tr>
                        <td>${income.amount.toFixed(2)}</td>
                        <td>${income.source}</td>
                        <td>${income.description}</td>
                        <td>${income.date}</td>
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