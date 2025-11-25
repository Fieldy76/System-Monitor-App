"""Application factory and initialization."""
# Import the Flask class to create the application instance
from flask import Flask
# Import Flask-Migrate for database migrations
from flask_migrate import Migrate

# Initialize Flask-Migrate instance (will be bound to app later)
migrate = Migrate()


def create_app(config_name='default'):
    """
    Application factory function.
    
    Args:
        config_name: Configuration to use ('development', 'testing', 'production', 'default')
    
    Returns:
        Flask application instance
    """
    # Initialize Flask app instance
    # __name__ tells Flask where to find resources like templates and static files
    app = Flask(__name__)
    
    # Load configuration from config.py
    # Import the config dictionary from the config module
    from config import config
    # Apply the selected configuration class to the app
    # This sets DEBUG, TESTING, SECRET_KEY, and other settings
    app.config.from_object(config[config_name])
    
    # Initialize Flask-Migrate with the app
    # This enables database migration commands (flask db init, migrate, upgrade)
    # Note: Requires a database to be configured in the future
    migrate.init_app(app)
    
    # Register blueprints
    # Import the main blueprint from the routes module
    from app.routes import main
    # Register the main blueprint with the app
    # This makes all routes defined in the blueprint available
    app.register_blueprint(main)
    
    # Return the configured Flask application instance
    return app
