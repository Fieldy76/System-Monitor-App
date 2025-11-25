"""Utility functions for checking external service health."""  # """Utility functions for checking external service health."""
import requests  # import requests
from datetime import datetime  # from datetime import datetime
from flask import current_app  # from flask import current_app
  # blank line
  # blank line
def check_http_service(url, name, timeout=5):  # def check_http_service(url, name, timeout=5):
    """  # """
    Check HTTP service health and return status.  # Check HTTP service health and return status.
      # blank line
    Args:  # Args:
        url: Service URL to check  # url: Service URL to check
        name: Service name for logging  # name: Service name for logging
        timeout: Request timeout in seconds  # timeout: Request timeout in seconds
          # blank line
    Returns:  # Returns:
        tuple: (is_up, status_code, response_time_ms, error_message)  # tuple: (is_up, status_code, response_time_ms, error_message)
    """  # """
    try:  # try:
        start_time = datetime.utcnow()  # start_time = datetime.utcnow()
        response = requests.get(url, timeout=timeout, allow_redirects=True)  # response = requests.get(url, timeout=timeout, allow_redirects=True)
        end_time = datetime.utcnow()  # end_time = datetime.utcnow()
          # blank line
        response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds  # response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
          # blank line
        # Consider 2xx and 3xx as successful  # # Consider 2xx and 3xx as successful
        is_up = 200 <= response.status_code < 400  # is_up = 200 <= response.status_code < 400
          # blank line
        return (is_up, response.status_code, response_time, None)  # return (is_up, response.status_code, response_time, None)
          # blank line
    except requests.exceptions.Timeout:  # except requests.exceptions.Timeout:
        return (False, None, None, f"Timeout after {timeout} seconds")  # return (False, None, None, f"Timeout after {timeout} seconds")
      # blank line
    except requests.exceptions.ConnectionError as e:  # except requests.exceptions.ConnectionError as e:
        return (False, None, None, f"Connection error: {str(e)}")  # return (False, None, None, f"Connection error: {str(e)}")
      # blank line
    except requests.exceptions.RequestException as e:  # except requests.exceptions.RequestException as e:
        return (False, None, None, f"Request failed: {str(e)}")  # return (False, None, None, f"Request failed: {str(e)}")
      # blank line
    except Exception as e:  # except Exception as e:
        current_app.logger.error(f"Unexpected error checking {name} ({url}): {e}")  # current_app.logger.error(f"Unexpected error checking {name} ({url}): {e}")
        return (False, None, None, f"Unexpected error: {str(e)}")  # return (False, None, None, f"Unexpected error: {str(e)}")
  # blank line
  # blank line
def check_tcp_service(host, port, timeout=5):  # def check_tcp_service(host, port, timeout=5):
    """  # """
    Check TCP service availability.  # Check TCP service availability.
      # blank line
    Args:  # Args:
        host: Hostname or IP address  # host: Hostname or IP address
        port: Port number  # port: Port number
        timeout: Connection timeout in seconds  # timeout: Connection timeout in seconds
          # blank line
    Returns:  # Returns:
        tuple: (is_up, response_time_ms, error_message)  # tuple: (is_up, response_time_ms, error_message)
    """  # """
    import socket  # import socket
      # blank line
    try:  # try:
        start_time = datetime.utcnow()  # start_time = datetime.utcnow()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)  # sock.settimeout(timeout)
          # blank line
        result = sock.connect_ex((host, port))  # result = sock.connect_ex((host, port))
        end_time = datetime.utcnow()  # end_time = datetime.utcnow()
        sock.close()  # sock.close()
          # blank line
        response_time = (end_time - start_time).total_seconds() * 1000  # response_time = (end_time - start_time).total_seconds() * 1000
          # blank line
        if result == 0:  # if result == 0:
            return (True, response_time, None)  # return (True, response_time, None)
        else:  # else:
            return (False, None, f"Connection refused (error code: {result})")  # return (False, None, f"Connection refused (error code: {result})")
              # blank line
    except socket.timeout:  # except socket.timeout:
        return (False, None, f"Timeout after {timeout} seconds")  # return (False, None, f"Timeout after {timeout} seconds")
      # blank line
    except socket.gaierror as e:  # except socket.gaierror as e:
        return (False, None, f"DNS resolution failed: {str(e)}")  # return (False, None, f"DNS resolution failed: {str(e)}")
      # blank line
    except Exception as e:  # except Exception as e:
        return (False, None, f"Unexpected error: {str(e)}")  # return (False, None, f"Unexpected error: {str(e)}")
  # blank line
  # blank line
def format_uptime_percentage(total_checks, successful_checks):  # def format_uptime_percentage(total_checks, successful_checks):
    """  # """
    Calculate uptime percentage.  # Calculate uptime percentage.
      # blank line
    Args:  # Args:
        total_checks: Total number of health checks performed  # total_checks: Total number of health checks performed
        successful_checks: Number of successful checks  # successful_checks: Number of successful checks
          # blank line
    Returns:  # Returns:
        float: Uptime percentage (0-100)  # float: Uptime percentage (0-100)
    """  # """
    if total_checks == 0:  # if total_checks == 0:
        return 100.0  # return 100.0
      # blank line
    return (successful_checks / total_checks) * 100  # return (successful_checks / total_checks) * 100
  # blank line
  # blank line
def get_service_status_color(is_up, response_time=None):  # def get_service_status_color(is_up, response_time=None):
    """  # """
    Get color code for service status visualization.  # Get color code for service status visualization.
      # blank line
    Args:  # Args:
        is_up: Boolean indicating if service is up  # is_up: Boolean indicating if service is up
        response_time: Response time in milliseconds (optional)  # response_time: Response time in milliseconds (optional)
          # blank line
    Returns:  # Returns:
        str: Color code ('green', 'yellow', 'red')  # str: Color code ('green', 'yellow', 'red')
    """  # """
    if not is_up:  # if not is_up:
        return 'red'  # return 'red'
      # blank line
    if response_time is None:  # if response_time is None:
        return 'green'  # return 'green'
      # blank line
    # Yellow if response time > 1000ms (1 second)  # # Yellow if response time > 1000ms (1 second)
    if response_time > 1000:  # if response_time > 1000:
        return 'yellow'  # return 'yellow'
      # blank line
    return 'green'  # return 'green'
