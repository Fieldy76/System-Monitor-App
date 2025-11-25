"""Configuration settings for different environments."""  # """Configuration settings for different environments."""
# Import os module to access environment variables  # # Import os module to access environment variables
import os  # import os
# Import load_dotenv to read variables from .env file  # # Import load_dotenv to read variables from .env file
from dotenv import load_dotenv  # from dotenv import load_dotenv
  # blank line
# Load environment variables from the .env file into os.environ  # # Load environment variables from the .env file into os.environ
# This allows us to access secrets and configuration without hardcoding them  # # This allows us to access secrets and configuration without hardcoding them
load_dotenv()  # load_dotenv()
  # blank line
  # blank line
class Config:  # class Config:
    """Base configuration class with common settings."""  # """Base configuration class with common settings."""
    # Get SECRET_KEY from environment variable, or use a default for development  # # Get SECRET_KEY from environment variable, or use a default for development
    # SECRET_KEY is used by Flask for session encryption and CSRF protection  # # SECRET_KEY is used by Flask for session encryption and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'  # SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
      # blank line
    # Flask settings  # # Flask settings
    # JSON_SORT_KEYS=False preserves the order of keys in JSON responses  # # JSON_SORT_KEYS=False preserves the order of keys in JSON responses
    JSON_SORT_KEYS = False  # JSON_SORT_KEYS = False
      # blank line
    # Database configuration  # # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///system_monitor.db'  # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///system_monitor.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # SQLALCHEMY_TRACK_MODIFICATIONS = False
      # blank line
    # Redis configuration for Celery  # # Redis configuration for Celery
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'  # REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL  # CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL  # CELERY_RESULT_BACKEND = REDIS_URL
      # blank line
    # Email configuration  # # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'  # MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)  # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']  # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@systemmonitor.com'  # MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@systemmonitor.com'
      # blank line
    # Twilio configuration for SMS alerts  # # Twilio configuration for SMS alerts
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')  # TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')  # TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')  # TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
      # blank line
    # Slack webhook configuration  # # Slack webhook configuration
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')  # SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
    SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#monitoring')  # SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#monitoring')
    SLACK_USERNAME = os.environ.get('SLACK_USERNAME', 'System Monitor Bot')  # SLACK_USERNAME = os.environ.get('SLACK_USERNAME', 'System Monitor Bot')
      # blank line
    # Monitoring settings  # # Monitoring settings
    METRIC_COLLECTION_INTERVAL = int(os.environ.get('METRIC_COLLECTION_INTERVAL', 60))  # seconds  # METRIC_COLLECTION_INTERVAL = int(os.environ.get('METRIC_COLLECTION_INTERVAL', 60))  # seconds
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 30))  # days  # DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 30))  # days
    ALERT_CHECK_INTERVAL = int(os.environ.get('ALERT_CHECK_INTERVAL', 60))  # seconds  # ALERT_CHECK_INTERVAL = int(os.environ.get('ALERT_CHECK_INTERVAL', 60))  # seconds
      # blank line
    # Pagination  # # Pagination
    ITEMS_PER_PAGE = 50  # ITEMS_PER_PAGE = 50
      # blank line
  # blank line
class DevelopmentConfig(Config):  # class DevelopmentConfig(Config):
    """Development environment configuration."""  # """Development environment configuration."""
    # DEBUG=True enables Flask's debug mode with auto-reload and detailed error pages  # # DEBUG=True enables Flask's debug mode with auto-reload and detailed error pages
    DEBUG = True  # DEBUG = True
    # TESTING=False indicates this is not a testing environment  # # TESTING=False indicates this is not a testing environment
    TESTING = False  # TESTING = False
  # blank line
  # blank line
class TestingConfig(Config):  # class TestingConfig(Config):
    """Testing environment configuration."""  # """Testing environment configuration."""
    # DEBUG=False disables debug mode during testing for more realistic conditions  # # DEBUG=False disables debug mode during testing for more realistic conditions
    DEBUG = False  # DEBUG = False
    # TESTING=True enables Flask's testing mode  # # TESTING=True enables Flask's testing mode
    TESTING = True  # TESTING = True
  # blank line
  # blank line
class ProductionConfig(Config):  # class ProductionConfig(Config):
    """Production environment configuration."""  # """Production environment configuration."""
    # DEBUG=False disables debug mode in production for security and performance  # # DEBUG=False disables debug mode in production for security and performance
    DEBUG = False  # DEBUG = False
    # TESTING=False indicates this is not a testing environment  # # TESTING=False indicates this is not a testing environment
    TESTING = False  # TESTING = False
      # blank line
    # In production, SECRET_KEY must be set via environment variable for security  # # In production, SECRET_KEY must be set via environment variable for security
    # Get the SECRET_KEY from environment variables  # # Get the SECRET_KEY from environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')  # SECRET_KEY = os.environ.get('SECRET_KEY')
    # If SECRET_KEY is not set, raise an error to prevent running without proper security  # # If SECRET_KEY is not set, raise an error to prevent running without proper security
    if not SECRET_KEY:  # if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")  # raise ValueError("SECRET_KEY environment variable must be set in production")
  # blank line
  # blank line
# Configuration dictionary mapping environment names to configuration classes  # # Configuration dictionary mapping environment names to configuration classes
# This allows easy selection of configuration based on environment  # # This allows easy selection of configuration based on environment
config = {  # config = {
    'development': DevelopmentConfig,  # Configuration for development environment  # 'development': DevelopmentConfig,  # Configuration for development environment
    'testing': TestingConfig,          # Configuration for testing environment  # 'testing': TestingConfig,          # Configuration for testing environment
    'production': ProductionConfig,    # Configuration for production environment  # 'production': ProductionConfig,    # Configuration for production environment
    'default': DevelopmentConfig       # Default configuration if none specified  # 'default': DevelopmentConfig       # Default configuration if none specified
}  # }
