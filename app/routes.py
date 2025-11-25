"""Routes and view logic using Flask Blueprints."""
# Import psutil library for retrieving system information
import psutil
# Import Flask utilities for creating blueprints, JSON responses, and rendering templates
from flask import Blueprint, jsonify, render_template

# Create blueprint named 'main' for organizing routes
# __name__ helps Flask determine the root path for the blueprint
main = Blueprint('main', __name__)


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    # Define the conversion factor (1024 bytes = 1 KB)
    factor = 1024
    # Iterate through units from Bytes to Petabytes
    for unit in ["", "K", "M", "G", "T", "P"]:
        # If the current bytes value is less than the factor, we found the right unit
        if bytes < factor:
            # Return the formatted string with 2 decimal places and the appropriate unit
            return f"{bytes:.2f}{unit}{suffix}"
        # Divide bytes by the factor to move to the next unit
        bytes /= factor


# Define route for the home page
@main.route('/')
def index():
    """Render the home page."""
    # Render and return the index.html template from the templates folder
    return render_template('index.html')


# Define API endpoint for system metrics
@main.route('/api/metrics')
def metrics():
    """API endpoint to get system metrics."""
    # Get CPU usage percentage
    # interval=None means it returns the utilization since the last call (non-blocking)
    cpu_percent = psutil.cpu_percent(interval=None)
    
    # Get CPU frequency information
    cpu_freq = psutil.cpu_freq()
    # Extract the current frequency if available, else set to 0
    cpu_freq_current = cpu_freq.current if cpu_freq else 0
    
    # Initialize CPU temperature variables to None
    cpu_temp_c = None
    cpu_temp_f = None
    try:
        # Retrieve temperatures from all hardware sensors
        temps = psutil.sensors_temperatures()
        # Check for 'coretemp' (common for Intel CPUs)
        if 'coretemp' in temps:
            # Get the current temperature of the first core/sensor in Celsius
            cpu_temp_c = temps['coretemp'][0].current
        # Check for 'cpu_thermal' (common for some Linux systems/Raspberry Pi)
        elif 'cpu_thermal' in temps:
            # Get the current temperature in Celsius
            cpu_temp_c = temps['cpu_thermal'][0].current
        # Check for 'k10temp' (common for AMD CPUs)
        elif 'k10temp' in temps:
            # Get the current temperature in Celsius
            cpu_temp_c = temps['k10temp'][0].current
            
        # If a temperature was successfully retrieved
        if cpu_temp_c is not None:
            # Convert Celsius to Fahrenheit using the formula: F = (C * 9/5) + 32
            cpu_temp_f = (cpu_temp_c * 9/5) + 32
    except Exception:
        # Ignore exceptions if sensor reading fails (e.g., on VMs or systems without sensors)
        pass

    # Get virtual memory usage statistics
    svmem = psutil.virtual_memory()
    # Create a dictionary with formatted memory stats
    memory_usage = {
        'total': get_size(svmem.total),      # Total physical memory
        'available': get_size(svmem.available), # Available memory
        'used': get_size(svmem.used),        # Used memory
        'percent': svmem.percent             # Percentage of memory used
    }

    # Get disk partitions information
    partitions = psutil.disk_partitions()
    # Initialize empty list to store disk usage information
    disk_usage_info = []
    # Iterate through each partition
    for partition in partitions:
        try:
            # Get disk usage statistics for the partition's mount point
            partition_usage = psutil.disk_usage(partition.mountpoint)
            # Append the partition details to the list
            disk_usage_info.append({
                'device': partition.device,          # Device path (e.g., /dev/sda1)
                'mountpoint': partition.mountpoint,  # Mount point path (e.g., /)
                'total': get_size(partition_usage.total), # Total size of partition
                'used': get_size(partition_usage.used),   # Used space on partition
                'free': get_size(partition_usage.free),   # Free space on partition
                'percent': partition_usage.percent        # Percentage of partition used
            })
        except PermissionError:
            # Skip partitions that throw a PermissionError (e.g., restricted system partitions)
            continue

    # Get disk I/O statistics
    disk_io = psutil.disk_io_counters()
    # Create a dictionary with formatted I/O stats
    disk_io_info = {
        'read_bytes': get_size(disk_io.read_bytes),   # Total bytes read from disk
        'write_bytes': get_size(disk_io.write_bytes), # Total bytes written to disk
        'read_count': disk_io.read_count,             # Total number of read operations
        'write_count': disk_io.write_count            # Total number of write operations
    }

    # Return all collected metrics as a JSON response
    return jsonify({
        'cpu': {
            'percent': cpu_percent,                    # CPU usage percentage
            'freq': f"{cpu_freq_current:.2f}Mhz",     # CPU frequency in MHz
            'temp_c': cpu_temp_c,                      # CPU temperature in Celsius
            'temp_f': cpu_temp_f                       # CPU temperature in Fahrenheit
        },
        'memory': memory_usage,    # Memory usage information
        'disk': disk_usage_info,   # Disk usage information for all partitions
        'io': disk_io_info         # Disk I/O statistics
    })
