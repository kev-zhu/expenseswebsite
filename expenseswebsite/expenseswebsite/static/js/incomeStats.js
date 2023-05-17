const renderChart = (data, labels) => {
    const ctx = document.getElementById('myChart');

    if (!data.length || !labels.length) {
        ctx.parentElement.removeChild(ctx)
    } else {
        var mychart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Last 6 months income',
                    data: data,
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'Income per category'
                    }
                },
                maintainAspectRatio: false
            }
        })
    }
    
}

const getChartData = () => {
    fetch('/income/income_source_summary')
    .then(res => res.json())
    .then(result => {
        const source_data = result.income_source_data
        const [labels, data] = [Object.keys(source_data), Object.values(source_data)]

        renderChart(data, labels)
    })
}

document.onload = getChartData()