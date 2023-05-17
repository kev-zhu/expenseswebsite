const renderChart = (data, labels) => {
    const ctx = document.getElementById('myChart');

    if (!data.length || !labels.length) {
        ctx.parentElement.removeChild(ctx)
    } else {
        var myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Last 6 months expenses',
                    data: data,
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'Expenses per category'
                    }
                },
                maintainAspectRatio: false
            }
        });
    }

    
}

const getChartData = () => {
    fetch('/expenses/expense_category_summary')
    .then(res => res.json())
    .then(result => {
        const category_data = result.expense_category_data
        const [labels, data] = [Object.keys(category_data), Object.values(category_data)]

        renderChart(data, labels)
    })
}

document.onload = getChartData()