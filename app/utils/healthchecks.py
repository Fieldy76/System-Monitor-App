"""Utility functions for checking external service health."""
import requests
from datetime import datetime, timezone
from flask import current_app


def check_http_service(url, name, timeout=5):
    """
    Check HTTP service health and return status.
    
    Args:
        url: Service URL to check
        name: Service name for logging
        timeout: Request timeout in seconds
        
    Returns:
        tuple: (is_up, status_code, response_time_ms, error_message)
    """
    try:
        start_time = datetime.now(timezone.utc)
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        end_time = datetime.now(timezone.utc)
        
        response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        # Consider 2xx and 3xx as successful
        is_up = 200 <= response.status_code < 400
        
        return (is_up, response.status_code, response_time, None)
        
    except requests.exceptions.Timeout:
        return (False, None, None, f"Timeout after {timeout} seconds")
    
    except requests.exceptions.ConnectionError as e:
        return (False, None, None, f"Connection error: {str(e)}")
    
    except requests.exceptions.RequestException as e:
        return (False, None, None, f"Request failed: {str(e)}")
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error checking {name} ({url}): {e}")
        return (False, None, None, f"Unexpected error: {str(e)}")


def check_tcp_service(host, port, timeout=5):
    """
    Check TCP service availability.
    
    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Connection timeout in seconds
        
    Returns:
        tuple: (is_up, response_time_ms, error_message)
    """
    import socket
    
    try:
        start_time = datetime.now(timezone.utc)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((host, port))
        end_time = datetime.now(timezone.utc)
        sock.close()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        
        if result == 0:
            return (True, response_time, None)
        else:
            return (False, None, f"Connection refused (error code: {result})")
            
    except socket.timeout:
        return (False, None, f"Timeout after {timeout} seconds")
    
    except socket.gaierror as e:
        return (False, None, f"DNS resolution failed: {str(e)}")
    
    except Exception as e:
        return (False, None, f"Unexpected error: {str(e)}")


def format_uptime_percentage(total_checks, successful_checks):
    """
    Calculate uptime percentage.
    
    Args:
        total_checks: Total number of health checks performed
        successful_checks: Number of successful checks
        
    Returns:
        float: Uptime percentage (0-100)
    """
    if total_checks == 0:
        return 100.0
    
    return (successful_checks / total_checks) * 100


def get_service_status_color(is_up, response_time=None):
    """
    Get color code for service status visualization.
    
    Args:
        is_up: Boolean indicating if service is up
        response_time: Response time in milliseconds (optional)
        
    Returns:
        str: Color code ('green', 'yellow', 'red')
    """
    if not is_up:
        return 'red'
    
    if response_time is None:
        return 'green'
    
    # Yellow if response time > 1000ms (1 second)
    if response_time > 1000:
        return 'yellow'
    
    return 'green'
