"""Tests for application routes."""
# Import json module to parse JSON responses
import json


def test_index_route(client):
    """Test that the home page loads successfully."""
    # Make a GET request to the home page route
    response = client.get('/')
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response contains HTML content
    # Check for either <!DOCTYPE html> or <html tag
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


def test_metrics_route(client):
    """Test that the metrics API endpoint returns valid JSON."""
    # Make a GET request to the metrics API endpoint
    response = client.get('/api/metrics')
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response content type is JSON
    assert response.content_type == 'application/json'
    
    # Parse JSON response into a Python dictionary
    data = json.loads(response.data)
    
    # Verify structure - check that all expected top-level keys are present
    assert 'cpu' in data      # CPU metrics should be present
    assert 'memory' in data   # Memory metrics should be present
    assert 'disk' in data     # Disk metrics should be present
    assert 'io' in data       # I/O metrics should be present
    
    # Verify CPU data structure
    assert 'percent' in data['cpu']  # CPU percentage should be present
    assert 'freq' in data['cpu']     # CPU frequency should be present
    
    # Verify memory data structure
    assert 'total' in data['memory']    # Total memory should be present
    assert 'used' in data['memory']     # Used memory should be present
    assert 'percent' in data['memory']  # Memory percentage should be present


def test_metrics_cpu_percent_range(client):
    """Test that CPU percent is within valid range."""
    # Make a GET request to the metrics API endpoint
    response = client.get('/api/metrics')
    # Parse the JSON response
    data = json.loads(response.data)
    
    # Extract the CPU percent value
    cpu_percent = data['cpu']['percent']
    # Assert that CPU percent is between 0 and 100 (inclusive)
    assert 0 <= cpu_percent <= 100


def test_metrics_memory_percent_range(client):
    """Test that memory percent is within valid range."""
    # Make a GET request to the metrics API endpoint
    response = client.get('/api/metrics')
    # Parse the JSON response
    data = json.loads(response.data)
    
    # Extract the memory percent value
    memory_percent = data['memory']['percent']
    # Assert that memory percent is between 0 and 100 (inclusive)
    assert 0 <= memory_percent <= 100
