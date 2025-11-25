"""Configuration settings for different environments."""
# Import os module to access environment variables
import os
# Import load_dotenv to read variables from .env file
from dotenv import load_dotenv

# Load environment variables from the .env file into os.environ
# This allows us to access secrets and configuration without hardcoding them
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    # Get SECRET_KEY from environment variable, or use a default for development
    # SECRET_KEY is used by Flask for session encryption and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Flask settings
    # JSON_SORT_KEYS=False preserves the order of keys in JSON responses
    JSON_SORT_KEYS = False
    
    # Add any common configuration here that applies to all environments
    

class DevelopmentConfig(Config):
    """Development environment configuration."""
    # DEBUG=True enables Flask's debug mode with auto-reload and detailed error pages
    DEBUG = True
    # TESTING=False indicates this is not a testing environment
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration."""
    # DEBUG=False disables debug mode during testing for more realistic conditions
    DEBUG = False
    # TESTING=True enables Flask's testing mode
    TESTING = True


class ProductionConfig(Config):
    """Production environment configuration."""
    # DEBUG=False disables debug mode in production for security and performance
    DEBUG = False
    # TESTING=False indicates this is not a testing environment
    TESTING = False
    
    # In production, SECRET_KEY must be set via environment variable for security
    # Get the SECRET_KEY from environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # If SECRET_KEY is not set, raise an error to prevent running without proper security
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


# Configuration dictionary mapping environment names to configuration classes
# This allows easy selection of configuration based on environment
config = {
    'development': DevelopmentConfig,  # Configuration for development environment
    'testing': TestingConfig,          # Configuration for testing environment
    'production': ProductionConfig,    # Configuration for production environment
    'default': DevelopmentConfig       # Default configuration if none specified
}
