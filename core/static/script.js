// GRAPH
const ctx = document.getElementById('resultGraph');
let forecastedSales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
const salesGraph = new Chart(ctx, {
    type: 'bar',
    data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [{
        label: '(Year) Sales Forecast',
        data: forecastedSales,
        borderWidth: 1
    }]
    },
    options: {
    scales: {
        y: {
        beginAtZero: true
        }
    },
    responsive: true
    }
}); 

// Find the index of the highest and lowest values
const highestValueIndex = forecastedSales.indexOf(Math.max(...forecastedSales));
const lowestValueIndex = forecastedSales.indexOf(Math.min(...forecastedSales));

// Define the colors for the highest, lowest, and default values
const highestColor = '#1a2dff';
const lowestColor = '#0099eb';
const defaultColor = '#0fb300';

// Update the backgroundColor and borderColor of the dataset
salesGraph.data.datasets[0].backgroundColor = forecastedSales.map((value, index) => {
return index === highestValueIndex ? highestColor : (index === lowestValueIndex ? lowestColor : defaultColor);
});

salesGraph.data.datasets[0].borderColor = salesGraph.data.datasets[0].backgroundColor;

// Update the chart/graph
salesGraph.update();


// BUTTON FUNCTIONS
const updateFileName = () => {
    const fileInput = document.getElementById('file-upload');
    const fileNameDisplay = document.getElementById('result-text');
    const fileErrorDisplay = document.getElementById('result-error');
    const processDataBtn = document.querySelector('.btn-process');
    
    if (fileInput.files.length > 0) {
        const fileName = fileInput.files[0].name;
        const fileExtension = fileName.split('.').pop();

        if (fileExtension.toLowerCase() !== 'csv' && fileExtension.toLowerCase() !== 'json') {
            fileErrorDisplay.innerText = 'Invalid file format.';
            fileInput.value = '';
            fileNameDisplay.innerText = '';
            processDataBtn.disabled = true;x
        } else {
            fileErrorDisplay.innerText = '';
            fileNameDisplay.innerText = 'Selected file: ' + fileName;
            processDataBtn.disabled = false;
        }
    } else {
        processDataBtn.disabled = true;
        fileNameDisplay.innerText = '';
        fileErrorDisplay.innerText = '';
    }
};

const resetData = () => {
    // Reset chart data
    forecastedSales.splice(0, forecastedSales.length, ...[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
    salesGraph.data.datasets[0].label = '(Year) Sales Forecast';
    salesGraph.update();

    // Reset text
    document.getElementById('result-text').innerText = '';
    document.getElementById('result-error').innerText = '';
    document.querySelector('.btn-process').disabled = true;
};

const processData = () => {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    const industryName = document.getElementsByName('industryname')[0].value;
    const resultText = document.getElementById('result-text');
    const resultError = document.getElementById('result-error');
    const processDataBtn = document.querySelector('.btn-process');

    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch(`http://localhost:8000/forecast/${industryName}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken, // Include the CSRF token in the headers
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                processDataBtn.disabled = true;
                resultText.innerText = data.message;
                resultError.innerText = '';

                // Update text dashboard
                let paragraphs = document.querySelectorAll('.monthly-sales-forecast');
                let totalSales = document.getElementById('total-sales');
                let highestSales = document.getElementById('highest-sales');
                let lowestSales = document.getElementById('lowest-sales');
                let averageSales = document.getElementById('average-sales');
                let highestSalesMonth = document.getElementById('highest-sales-month');
                let lowestSalesMonth = document.getElementById('lowest-sales-month');
                for (let i = 0; i < data.predictions.length; i++) {
                    paragraphs[i].textContent = `${data.predictions[i].toLocaleString()}`;
                }
                totalSales.textContent = `${data.total_sales.toLocaleString()}`;
                highestSales.textContent = `${data.highest_sales[0].toLocaleString()}`;
                lowestSales.textContent = `${data.lowest_sales[0].toLocaleString()}`;
                averageSales.textContent = `${data.average_sales.toLocaleString()}`;
                highestSalesMonth.textContent = data.highest_sales[1];
                lowestSalesMonth.textContent = data.lowest_sales[1];

                // Update chart/graph
                // Update year
                salesGraph.data.datasets[0].label = `${data.predicted_year} Sales Forecast`;

                // Update the forecastedSales array with new data
                forecastedSales.splice(0, forecastedSales.length, ...data.predictions);

                // Recalculate the index of the highest and lowest values
                const highestValueIndex = forecastedSales.indexOf(Math.max(...forecastedSales));
                const lowestValueIndex = forecastedSales.indexOf(Math.min(...forecastedSales));

                // Update the backgroundColor and borderColor of the dataset
                salesGraph.data.datasets[0].backgroundColor = forecastedSales.map((value, index) => {
                    return index === highestValueIndex ? highestColor : (index === lowestValueIndex ? lowestColor : defaultColor);
                });

                salesGraph.data.datasets[0].borderColor = salesGraph.data.datasets[0].backgroundColor;

                // Update the chart/graph
                salesGraph.update();
            } else {
                resultText.innerText = '';
                resultError.innerText = data.message;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
};