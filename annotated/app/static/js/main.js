// Chart Configuration  // // Chart Configuration
// Define common options for all Chart.js instances  // // Define common options for all Chart.js instances
const commonOptions = {  // const commonOptions = {
    // Make the chart responsive to window resizing  // // Make the chart responsive to window resizing
    responsive: true,  // responsive: true,
    // Allow the chart to fill the container height  // // Allow the chart to fill the container height
    maintainAspectRatio: false,  // maintainAspectRatio: false,
    // Configuration for chart plugins  // // Configuration for chart plugins
    plugins: {  // plugins: {
        // Hide the legend  // // Hide the legend
        legend: { display: false },  // legend: { display: false },
        // Configure tooltips  // // Configure tooltips
        tooltip: {  // tooltip: {
            // Show tooltip for all items at the same index  // // Show tooltip for all items at the same index
            mode: 'index',  // mode: 'index',
            // Show tooltip even if not directly hovering over a point  // // Show tooltip even if not directly hovering over a point
            intersect: false,  // intersect: false,
            // Set tooltip background color  // // Set tooltip background color
            backgroundColor: 'rgba(15, 23, 42, 0.9)',  // backgroundColor: 'rgba(15, 23, 42, 0.9)',
            // Set tooltip title color  // // Set tooltip title color
            titleColor: '#f8fafc',  // titleColor: '#f8fafc',
            // Set tooltip body text color  // // Set tooltip body text color
            bodyColor: '#cbd5e1',  // bodyColor: '#cbd5e1',
            // Set tooltip border color  // // Set tooltip border color
            borderColor: 'rgba(255, 255, 255, 0.1)',  // borderColor: 'rgba(255, 255, 255, 0.1)',
            // Set tooltip border width  // // Set tooltip border width
            borderWidth: 1  // borderWidth: 1
        }  // }
    },  // },
    // Configuration for chart scales (axes)  // // Configuration for chart scales (axes)
    scales: {  // scales: {
        // X-axis configuration  // // X-axis configuration
        x: {  // x: {
            // Hide the X-axis labels  // // Hide the X-axis labels
            display: false,  // display: false,
            // Hide the X-axis grid lines  // // Hide the X-axis grid lines
            grid: { display: false }  // grid: { display: false }
        },  // },
        // Y-axis configuration  // // Y-axis configuration
        y: {  // y: {
            // Show the Y-axis labels  // // Show the Y-axis labels
            display: true,  // display: true,
            // Start the Y-axis at 0  // // Start the Y-axis at 0
            beginAtZero: true,  // beginAtZero: true,
            // Set the maximum value for the Y-axis to 100 (percentage)  // // Set the maximum value for the Y-axis to 100 (percentage)
            max: 100,  // max: 100,
            // Grid line configuration  // // Grid line configuration
            grid: {  // grid: {
                // Set grid line color  // // Set grid line color
                color: 'rgba(255, 255, 255, 0.05)',  // color: 'rgba(255, 255, 255, 0.05)',
                // Do not draw the border line on the axis  // // Do not draw the border line on the axis
                drawBorder: false  // drawBorder: false
            },  // },
            // Tick label configuration  // // Tick label configuration
            ticks: {  // ticks: {
                // Set tick label color  // // Set tick label color
                color: '#64748b',  // color: '#64748b',
                // Set tick font size  // // Set tick font size
                font: { size: 10 }  // font: { size: 10 }
            }  // }
        }  // }
    },  // },
    // Configuration for chart elements  // // Configuration for chart elements
    elements: {  // elements: {
        // Point configuration  // // Point configuration
        point: { radius: 0, hitRadius: 10 }, // Hide points but keep them interactable  // point: { radius: 0, hitRadius: 10 }, // Hide points but keep them interactable
        // Line configuration  // // Line configuration
        line: { tension: 0.4 } // Add a slight curve to the line (smoothing)  // line: { tension: 0.4 } // Add a slight curve to the line (smoothing)
    },  // },
    // Animation configuration  // // Animation configuration
    animation: { duration: 0 } // Disable animation for smooth real-time updates  // animation: { duration: 0 } // Disable animation for smooth real-time updates
};  // };
  // blank line
// Initialize Charts  // // Initialize Charts
// Get the 2D context for the CPU chart canvas  // // Get the 2D context for the CPU chart canvas
const cpuCtx = document.getElementById('cpuChart').getContext('2d');  // const cpuCtx = document.getElementById('cpuChart').getContext('2d');
// Get the 2D context for the Memory chart canvas  // // Get the 2D context for the Memory chart canvas
const memoryCtx = document.getElementById('memoryChart').getContext('2d');  // const memoryCtx = document.getElementById('memoryChart').getContext('2d');
  // blank line
// Helper function to create a linear gradient for the chart background  // // Helper function to create a linear gradient for the chart background
const createGradient = (ctx, colorStart, colorEnd) => {  // const createGradient = (ctx, colorStart, colorEnd) => {
    // Create a linear gradient from top to bottom  // // Create a linear gradient from top to bottom
    const gradient = ctx.createLinearGradient(0, 0, 0, 150);  // const gradient = ctx.createLinearGradient(0, 0, 0, 150);
    // Add the start color at the top  // // Add the start color at the top
    gradient.addColorStop(0, colorStart);  // gradient.addColorStop(0, colorStart);
    // Add the end color at the bottom  // // Add the end color at the bottom
    gradient.addColorStop(1, colorEnd);  // gradient.addColorStop(1, colorEnd);
    // Return the created gradient  // // Return the created gradient
    return gradient;  // return gradient;
};  // };
  // blank line
// Create the CPU Chart instance  // // Create the CPU Chart instance
const cpuChart = new Chart(cpuCtx, {  // const cpuChart = new Chart(cpuCtx, {
    // Set chart type to line  // // Set chart type to line
    type: 'line',  // type: 'line',
    // Data configuration  // // Data configuration
    data: {  // data: {
        // Initialize labels with empty strings (for 60 data points)  // // Initialize labels with empty strings (for 60 data points)
        labels: Array(60).fill(''),  // labels: Array(60).fill(''),
        // Dataset configuration  // // Dataset configuration
        datasets: [{  // datasets: [{
            // Label for the dataset  // // Label for the dataset
            label: 'CPU Usage',  // label: 'CPU Usage',
            // Initialize data with 0s (for 60 data points)  // // Initialize data with 0s (for 60 data points)
            data: Array(60).fill(0),  // data: Array(60).fill(0),
            // Set line color  // // Set line color
            borderColor: '#38bdf8',  // borderColor: '#38bdf8',
            // Set background color (gradient)  // // Set background color (gradient)
            backgroundColor: createGradient(cpuCtx, 'rgba(56, 189, 248, 0.5)', 'rgba(56, 189, 248, 0.0)'),  // backgroundColor: createGradient(cpuCtx, 'rgba(56, 189, 248, 0.5)', 'rgba(56, 189, 248, 0.0)'),
            // Fill the area under the line  // // Fill the area under the line
            fill: true,  // fill: true,
            // Set line width  // // Set line width
            borderWidth: 2  // borderWidth: 2
        }]  // }]
    },  // },
    // Apply common options  // // Apply common options
    options: commonOptions  // options: commonOptions
});  // });
  // blank line
// Create the Memory Chart instance  // // Create the Memory Chart instance
const memoryChart = new Chart(memoryCtx, {  // const memoryChart = new Chart(memoryCtx, {
    // Set chart type to line  // // Set chart type to line
    type: 'line',  // type: 'line',
    // Data configuration  // // Data configuration
    data: {  // data: {
        // Initialize labels with empty strings  // // Initialize labels with empty strings
        labels: Array(60).fill(''),  // labels: Array(60).fill(''),
        // Dataset configuration  // // Dataset configuration
        datasets: [{  // datasets: [{
            // Label for the dataset  // // Label for the dataset
            label: 'Memory Usage',  // label: 'Memory Usage',
            // Initialize data with 0s  // // Initialize data with 0s
            data: Array(60).fill(0),  // data: Array(60).fill(0),
            // Set line color  // // Set line color
            borderColor: '#a855f7',  // borderColor: '#a855f7',
            // Set background color (gradient)  // // Set background color (gradient)
            backgroundColor: createGradient(memoryCtx, 'rgba(168, 85, 247, 0.5)', 'rgba(168, 85, 247, 0.0)'),  // backgroundColor: createGradient(memoryCtx, 'rgba(168, 85, 247, 0.5)', 'rgba(168, 85, 247, 0.0)'),
            // Fill the area under the line  // // Fill the area under the line
            fill: true,  // fill: true,
            // Set line width  // // Set line width
            borderWidth: 2  // borderWidth: 2
        }]  // }]
    },  // },
    // Apply common options  // // Apply common options
    options: commonOptions  // options: commonOptions
});  // });
  // blank line
// Data Fetching and Updating  // // Data Fetching and Updating
// Async function to fetch metrics from the backend  // // Async function to fetch metrics from the backend
async function fetchMetrics() {  // async function fetchMetrics() {
    try {  // try {
        // Make a GET request to the metrics API endpoint  // // Make a GET request to the metrics API endpoint
        const response = await fetch('/api/metrics');  // const response = await fetch('/api/metrics');
        // Parse the JSON response  // // Parse the JSON response
        const data = await response.json();  // const data = await response.json();
        // Update the dashboard with the fetched data  // // Update the dashboard with the fetched data
        updateDashboard(data);  // updateDashboard(data);
    } catch (error) {  // } catch (error) {
        // Log any errors to the console  // // Log any errors to the console
        console.error('Error fetching metrics:', error);  // console.error('Error fetching metrics:', error);
    }  // }
}  // }
  // blank line
// Function to update the DOM elements with new data  // // Function to update the DOM elements with new data
function updateDashboard(data) {  // function updateDashboard(data) {
    // Update CPU Section  // // Update CPU Section
    // Set CPU percentage text  // // Set CPU percentage text
    document.getElementById('cpu-percent').textContent = data.cpu.percent;  // document.getElementById('cpu-percent').textContent = data.cpu.percent;
    // Set CPU frequency text  // // Set CPU frequency text
    document.getElementById('cpu-freq').textContent = data.cpu.freq;  // document.getElementById('cpu-freq').textContent = data.cpu.freq;
  // blank line
    // Initialize temperature text  // // Initialize temperature text
    let tempText = '--';  // let tempText = '--';
    // Check if temperature data is available  // // Check if temperature data is available
    if (data.cpu.temp_c !== null) {  // if (data.cpu.temp_c !== null) {
        // Format temperature string with Celsius and Fahrenheit  // // Format temperature string with Celsius and Fahrenheit
        tempText = `${data.cpu.temp_c.toFixed(1)}°C / ${data.cpu.temp_f.toFixed(1)}°F`;  // tempText = `${data.cpu.temp_c.toFixed(1)}°C / ${data.cpu.temp_f.toFixed(1)}°F`;
    }  // }
    // Set CPU temperature text  // // Set CPU temperature text
    document.getElementById('cpu-temp').textContent = tempText;  // document.getElementById('cpu-temp').textContent = tempText;
  // blank line
    // Update the CPU chart with the new percentage  // // Update the CPU chart with the new percentage
    updateChart(cpuChart, data.cpu.percent);  // updateChart(cpuChart, data.cpu.percent);
  // blank line
    // Update Memory Section  // // Update Memory Section
    // Set Memory percentage text  // // Set Memory percentage text
    document.getElementById('mem-percent').textContent = data.memory.percent;  // document.getElementById('mem-percent').textContent = data.memory.percent;
    // Set Memory used text  // // Set Memory used text
    document.getElementById('mem-used').textContent = data.memory.used;  // document.getElementById('mem-used').textContent = data.memory.used;
    // Set Memory total text  // // Set Memory total text
    document.getElementById('mem-total').textContent = data.memory.total;  // document.getElementById('mem-total').textContent = data.memory.total;
  // blank line
    // Update the Memory chart with the new percentage  // // Update the Memory chart with the new percentage
    updateChart(memoryChart, data.memory.percent);  // updateChart(memoryChart, data.memory.percent);
  // blank line
    // Update IO Section  // // Update IO Section
    // Set Read bytes text  // // Set Read bytes text
    document.getElementById('io-read').textContent = data.io.read_bytes;  // document.getElementById('io-read').textContent = data.io.read_bytes;
    // Set Write bytes text  // // Set Write bytes text
    document.getElementById('io-write').textContent = data.io.write_bytes;  // document.getElementById('io-write').textContent = data.io.write_bytes;
  // blank line
    // Update Disk Usage Section  // // Update Disk Usage Section
    // Get the container for disk items  // // Get the container for disk items
    const diskContainer = document.getElementById('disk-container');  // const diskContainer = document.getElementById('disk-container');
    // Clear existing disk items  // // Clear existing disk items
    diskContainer.innerHTML = ''; // Clear existing  // diskContainer.innerHTML = ''; // Clear existing
  // blank line
    // Iterate through each disk in the data  // // Iterate through each disk in the data
    data.disk.forEach(disk => {  // data.disk.forEach(disk => {
        // Create a new div for the disk item  // // Create a new div for the disk item
        const diskItem = document.createElement('div');  // const diskItem = document.createElement('div');
        // Set the class name  // // Set the class name
        diskItem.className = 'disk-item';  // diskItem.className = 'disk-item';
        // Set the inner HTML with disk details and progress bar  // // Set the inner HTML with disk details and progress bar
        diskItem.innerHTML = `  // diskItem.innerHTML = `
            <div class="disk-header">  // <div class="disk-header">
                <span>${disk.mountpoint} (${disk.device})</span>  // <span>${disk.mountpoint} (${disk.device})</span>
                <span>${disk.used} / ${disk.total}</span>  // <span>${disk.used} / ${disk.total}</span>
            </div>  // </div>
            <div class="disk-bar-bg">  // <div class="disk-bar-bg">
                <div class="disk-bar-fill" style="width: ${disk.percent}%"></div>  // <div class="disk-bar-fill" style="width: ${disk.percent}%"></div>
            </div>  // </div>
        `;  // `;
        // Append the disk item to the container  // // Append the disk item to the container
        diskContainer.appendChild(diskItem);  // diskContainer.appendChild(diskItem);
    });  // });
}  // }
  // blank line
// Function to update a chart with a new value  // // Function to update a chart with a new value
function updateChart(chart, newValue) {  // function updateChart(chart, newValue) {
    // Get the data array from the first dataset  // // Get the data array from the first dataset
    const data = chart.data.datasets[0].data;  // const data = chart.data.datasets[0].data;
    // Add the new value to the end of the array  // // Add the new value to the end of the array
    data.push(newValue);  // data.push(newValue);
    // Remove the oldest value from the beginning of the array  // // Remove the oldest value from the beginning of the array
    data.shift(); // Remove oldest  // data.shift(); // Remove oldest
    // Update the chart to reflect changes  // // Update the chart to reflect changes
    chart.update();  // chart.update();
}  // }
  // blank line
// Start polling  // // Start polling
// Set an interval to fetch metrics every 1000ms (1 second)  // // Set an interval to fetch metrics every 1000ms (1 second)
setInterval(fetchMetrics, 1000);  // setInterval(fetchMetrics, 1000);
// Perform the initial fetch immediately  // // Perform the initial fetch immediately
fetchMetrics(); // Initial call  // fetchMetrics(); // Initial call
