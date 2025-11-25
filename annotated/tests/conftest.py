"""Pytest configuration and fixtures."""  # """Pytest configuration and fixtures."""
# Import pytest for creating test fixtures  # # Import pytest for creating test fixtures
import pytest  # import pytest
# Import the create_app factory function to create test application instances  # # Import the create_app factory function to create test application instances
from app import create_app  # from app import create_app
  # blank line
  # blank line
# Define a pytest fixture for creating the application instance  # # Define a pytest fixture for creating the application instance
@pytest.fixture  # @pytest.fixture
def app():  # def app():
    """Create application instance for testing."""  # """Create application instance for testing."""
    # Create and return a Flask app using the 'testing' configuration  # # Create and return a Flask app using the 'testing' configuration
    # This ensures DEBUG=False and TESTING=True for proper test conditions  # # This ensures DEBUG=False and TESTING=True for proper test conditions
    app = create_app('testing')  # app = create_app('testing')
    return app  # return app
  # blank line
  # blank line
# Define a pytest fixture for creating a test client  # # Define a pytest fixture for creating a test client
@pytest.fixture  # @pytest.fixture
def client(app):  # def client(app):
    """Create test client."""  # """Create test client."""
    # Return a test client for the app  # # Return a test client for the app
    # This allows making HTTP requests to the app in tests without running a server  # # This allows making HTTP requests to the app in tests without running a server
    return app.test_client()  # return app.test_client()
  # blank line
  # blank line
# Define a pytest fixture for creating a CLI test runner  # # Define a pytest fixture for creating a CLI test runner
@pytest.fixture  # @pytest.fixture
def runner(app):  # def runner(app):
    """Create test CLI runner."""  # """Create test CLI runner."""
    # Return a CLI runner for testing Flask CLI commands  # # Return a CLI runner for testing Flask CLI commands
    return app.test_cli_runner()  # return app.test_cli_runner()
