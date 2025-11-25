"""Application entry point."""  # """Application entry point."""
# Import the os module to access environment variables  # # Import the os module to access environment variables
import os  # import os
# Import the create_app factory function from the app package  # # Import the create_app factory function from the app package
from app import create_app  # from app import create_app
  # blank line
# Get the environment name from the FLASK_ENV environment variable  # # Get the environment name from the FLASK_ENV environment variable
# If FLASK_ENV is not set, default to 'development'  # # If FLASK_ENV is not set, default to 'development'
config_name = os.environ.get('FLASK_ENV', 'development')  # config_name = os.environ.get('FLASK_ENV', 'development')
  # blank line
# Create the Flask application instance using the factory function  # # Create the Flask application instance using the factory function
# Pass the config_name to load the appropriate configuration (dev/test/prod)  # # Pass the config_name to load the appropriate configuration (dev/test/prod)
app = create_app(config_name)  # app = create_app(config_name)
  # blank line
# Check if this script is being run directly (not imported as a module)  # # Check if this script is being run directly (not imported as a module)
if __name__ == '__main__':  # if __name__ == '__main__':
    # Run the Flask development server  # # Run the Flask development server
    # debug=True enables debug mode with auto-reload and detailed error pages  # # debug=True enables debug mode with auto-reload and detailed error pages
    # host='0.0.0.0' makes the server accessible from any network interface  # # host='0.0.0.0' makes the server accessible from any network interface
    # port=5000 sets the server to listen on port 5000  # # port=5000 sets the server to listen on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)  # app.run(debug=True, host='0.0.0.0', port=5000)
