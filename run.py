"""Application entry point."""
# Import the os module to access environment variables
import os
# Import the create_app factory function from the app package
from app import create_app

# Get the environment name from the FLASK_ENV environment variable
# If FLASK_ENV is not set, default to 'development'
config_name = os.environ.get('FLASK_ENV', 'development')

# Create the Flask application instance using the factory function
# Pass the config_name to load the appropriate configuration (dev/test/prod)
app = create_app(config_name)

# Check if this script is being run directly (not imported as a module)
if __name__ == '__main__':
    # Run the Flask development server
    # debug=True enables debug mode with auto-reload and detailed error pages
    # host='0.0.0.0' makes the server accessible from any network interface
    # port=5000 sets the server to listen on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
