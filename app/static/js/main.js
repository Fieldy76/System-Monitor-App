// Chart Configuration
// Define common options for all Chart.js instances
const commonOptions = {
    // Make the chart responsive to window resizing
    responsive: true,
    // Allow the chart to fill the container height
    maintainAspectRatio: false,
    // Configuration for chart plugins
    plugins: {
        // Hide the legend
        legend: { display: false },
        // Configure tooltips
        tooltip: {
            // Show tooltip for all items at the same index
            mode: 'index',
            // Show tooltip even if not directly hovering over a point
            intersect: false,
            // Set tooltip background color
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            // Set tooltip title color
            titleColor: '#f8fafc',
            // Set tooltip body text color
            bodyColor: '#cbd5e1',
            // Set tooltip border color
            borderColor: 'rgba(255, 255, 255, 0.1)',
            // Set tooltip border width
            borderWidth: 1
        }
    },
    // Configuration for chart scales (axes)
    scales: {
        // X-axis configuration
        x: {
            // Hide the X-axis labels
            display: false,
            // Hide the X-axis grid lines
            grid: { display: false }
        },
        // Y-axis configuration
        y: {
            // Show the Y-axis labels
            display: true,
            // Start the Y-axis at 0
            beginAtZero: true,
            // Set the maximum value for the Y-axis to 100 (percentage)
            max: 100,
            // Grid line configuration
            grid: {
                // Set grid line color
                color: 'rgba(255, 255, 255, 0.05)',
                // Do not draw the border line on the axis
                drawBorder: false
            },
            // Tick label configuration
            ticks: {
                // Set tick label color
                color: '#64748b',
                // Set tick font size
                font: { size: 10 }
            }
        }
    },
    // Configuration for chart elements
    elements: {
        // Point configuration
        point: { radius: 0, hitRadius: 10 }, // Hide points but keep them interactable
        // Line configuration
        line: { tension: 0.4 } // Add a slight curve to the line (smoothing)
    },
    // Animation configuration
    animation: { duration: 0 } // Disable animation for smooth real-time updates
};

// Initialize Charts
// Get the 2D context for the CPU chart canvas
const cpuCtx = document.getElementById('cpuChart').getContext('2d');
// Get the 2D context for the Memory chart canvas
const memoryCtx = document.getElementById('memoryChart').getContext('2d');
// Get the 2D context for the IO chart canvas
const ioCtx = document.getElementById('ioChart').getContext('2d');

// Helper function to create a linear gradient for the chart background
const createGradient = (ctx, colorStart, colorEnd) => {
    // Create a linear gradient from top to bottom
    const gradient = ctx.createLinearGradient(0, 0, 0, 150);
    // Add the start color at the top
    gradient.addColorStop(0, colorStart);
    // Add the end color at the bottom
    gradient.addColorStop(1, colorEnd);
    // Return the created gradient
    return gradient;
};

// Create the CPU Chart instance
const cpuChart = new Chart(cpuCtx, {
    // Set chart type to line
    type: 'line',
    // Data configuration
    data: {
        // Initialize labels with empty strings (for 60 data points)
        labels: Array(60).fill(''),
        // Dataset configuration
        datasets: [{
            // Label for the dataset
            label: 'CPU Usage',
            // Initialize data with 0s (for 60 data points)
            data: Array(60).fill(0),
            // Set line color
            borderColor: '#38bdf8',
            // Set background color (gradient)
            backgroundColor: createGradient(cpuCtx, 'rgba(56, 189, 248, 0.5)', 'rgba(56, 189, 248, 0.0)'),
            // Fill the area under the line
            fill: true,
            // Set line width
            borderWidth: 2
        }]
    },
    // Apply common options
    options: commonOptions
});

// Create the Memory Chart instance
const memoryChart = new Chart(memoryCtx, {
    // Set chart type to line
    type: 'line',
    // Data configuration
    data: {
        // Initialize labels with empty strings
        labels: Array(60).fill(''),
        // Dataset configuration
        datasets: [{
            // Label for the dataset
            label: 'Memory Usage',
            // Initialize data with 0s
            data: Array(60).fill(0),
            // Set line color
            borderColor: '#a855f7',
            // Set background color (gradient)
            backgroundColor: createGradient(memoryCtx, 'rgba(168, 85, 247, 0.5)', 'rgba(168, 85, 247, 0.0)'),
            // Fill the area under the line
            fill: true,
            // Set line width
            borderWidth: 2
        }]
    },
    // Apply common options
    options: commonOptions
});

// Data Fetching and Updating
// Async function to fetch metrics from the backend
async function fetchMetrics() {
    try {
        // Make a GET request to the metrics API endpoint
        const response = await fetch('/api/metrics');
        // Parse the JSON response
        const data = await response.json();
        // Update the dashboard with the fetched data
        updateDashboard(data);
    } catch (error) {
        // Log any errors to the console
        console.error('Error fetching metrics:', error);
    }
}

// Function to update the DOM elements with new data
function updateDashboard(data) {
    // Update CPU Section
    // Set CPU percentage text
    document.getElementById('cpu-percent').textContent = data.cpu.percent;
    // Set CPU frequency text
    document.getElementById('cpu-freq').textContent = data.cpu.freq;

    // Initialize temperature text
    let tempText = '--';
    // Check if temperature data is available
    if (data.cpu.temp_c !== null) {
        // Format temperature string with Celsius and Fahrenheit
        tempText = `${data.cpu.temp_c.toFixed(1)}°C / ${data.cpu.temp_f.toFixed(1)}°F`;
    }
    // Set CPU temperature text
    document.getElementById('cpu-temp').textContent = tempText;

    // Update the CPU chart with the new percentage
    updateChart(cpuChart, data.cpu.percent);

    // Update Memory Section
    // Set Memory percentage text
    document.getElementById('mem-percent').textContent = data.memory.percent;
    // Set Memory used text
    document.getElementById('mem-used').textContent = data.memory.used;
    // Set Memory total text
    document.getElementById('mem-total').textContent = data.memory.total;

    // Update the Memory chart with the new percentage
    updateChart(memoryChart, data.memory.percent);

    // Update IO Section
    // Set Read bytes text
    document.getElementById('io-read').textContent = data.io.read_bytes;
    // Set Write bytes text
    document.getElementById('io-write').textContent = data.io.write_bytes;

    // Update Disk Usage Section
    // Get the container for disk items
    const diskContainer = document.getElementById('disk-container');
    // Clear existing disk items
    diskContainer.innerHTML = ''; // Clear existing

    // Iterate through each disk in the data
    data.disk.forEach(disk => {
        // Create a new div for the disk item
        const diskItem = document.createElement('div');
        // Set the class name
        diskItem.className = 'disk-item';
        // Set the inner HTML with disk details and progress bar
        diskItem.innerHTML = `
            <div class="disk-header">
                <span>${disk.mountpoint} (${disk.device})</span>
                <span>${disk.used} / ${disk.total}</span>
            </div>
            <div class="disk-bar-bg">
                <div class="disk-bar-fill" style="width: ${disk.percent}%"></div>
            </div>
        `;
        // Append the disk item to the container
        diskContainer.appendChild(diskItem);
    });
}

// Function to update a chart with a new value
function updateChart(chart, newValue) {
    // Get the data array from the first dataset
    const data = chart.data.datasets[0].data;
    // Add the new value to the end of the array
    data.push(newValue);
    // Remove the oldest value from the beginning of the array
    data.shift(); // Remove oldest
    // Update the chart to reflect changes
    chart.update();
}

// Start polling
// Set an interval to fetch metrics every 1000ms (1 second)
setInterval(fetchMetrics, 1000);
// Perform the initial fetch immediately
fetchMetrics(); // Initial call
