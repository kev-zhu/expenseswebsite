const getBackgroundColor = (data) => {
    color = []
    data.forEach(amount => {
        if (amount < 0) {
            color.push('#F4D9D9')
        } else {
            color.push('#DFF4D9')
        }
    })
    return color
}

const calcLineData = (total_prior_year, data) => {
    adjustedData = []
    total = total_prior_year
    data.forEach(amount => {
        total += amount
        adjustedData.push(total)
    })
    return adjustedData
}

const renderCharts = (total_prior_year, data, labels) => {
    const barChart = document.getElementById('barChart')
    const lineChart = document.getElementById('lineChart')

    var myChart = new Chart(barChart, {
        type: 'bar',
        data: {
            //color for bars -- red if negative, green if positive
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: getBackgroundColor(data)
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Total Gain/Loss per Month'
                },
                legend: {
                    display: false
                }
            },
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    })

    var myChart = new Chart(lineChart, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: calcLineData(total_prior_year, data),
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Change in Networth per Month'
                },
                legend: {
                    display: false
                }
            },
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    })
}

const getChartData = () => {
    fetch('/get-one-year-data')
    .then(res => res.json())
    .then(result => {
        const result_data = result.data
        const total_prior_year = result.total_prior_year
        const [labels, data] = [Object.keys(result_data), Object.values(result_data)]

        renderCharts(total_prior_year, data, labels)
    })
}

document.onload = getChartData()