"""Application factory and initialization."""
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS

# Initialize extensions (db is imported from models)
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()


def create_app(config_name='default', config_object=None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration to use ('development', 'testing', 'production', 'default')
        config_object: Optional configuration object to use directly (overrides config_name)
    
    Returns:
        Flask application instance
    """
    # Initialize Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        from config import config
        app.config.from_object(config[config_name])
    
    # Initialize database
    from app.models import db
    db.init_app(app)
    
    # Initialize Flask-Migrate with the app and database
    migrate.init_app(app, db)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize CORS for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    from app.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    
    # Initialize background scheduler
    from app.tasks import init_scheduler
    init_scheduler(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        # Create local server entry if it doesn't exist
        from app.models import Server
        local_server = Server.query.filter_by(is_local=True).first()
        if not local_server:
            import secrets
            local_server = Server(
                name='Local Server',
                hostname='localhost',
                api_key=secrets.token_urlsafe(32),
                is_local=True,
                is_active=True
            )
            db.session.add(local_server)
            db.session.commit()
    
    return app

