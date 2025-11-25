"""Pytest configuration and fixtures."""
# Import pytest for creating test fixtures
import pytest
# Import the create_app factory function to create test application instances
from app import create_app


# Define a pytest fixture for creating the application instance
@pytest.fixture
def app():
    """Create application instance for testing."""
    # Create and return a Flask app using the 'testing' configuration
    # This ensures DEBUG=False and TESTING=True for proper test conditions
    app = create_app('testing')
    return app


# Define a pytest fixture for creating a test client
@pytest.fixture
def client(app):
    """Create test client."""
    # Return a test client for the app
    # This allows making HTTP requests to the app in tests without running a server
    return app.test_client()


# Define a pytest fixture for creating a CLI test runner
@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    # Return a CLI runner for testing Flask CLI commands
    return app.test_cli_runner()
