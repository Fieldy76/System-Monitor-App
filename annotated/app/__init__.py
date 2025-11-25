"""Application factory and initialization."""  # """Application factory and initialization."""
from flask import Flask  # from flask import Flask
from flask_migrate import Migrate  # from flask_migrate import Migrate
from flask_login import LoginManager  # from flask_login import LoginManager
from flask_mail import Mail  # from flask_mail import Mail
from flask_cors import CORS  # from flask_cors import CORS
  # blank line
# Initialize extensions (db is imported from models)  # # Initialize extensions (db is imported from models)
migrate = Migrate()  # migrate = Migrate()
login_manager = LoginManager()  # login_manager = LoginManager()
mail = Mail()  # mail = Mail()
  # blank line
  # blank line
def create_app(config_name='default', config_object=None):  # def create_app(config_name='default', config_object=None):
    """  # """
    Application factory function.  # Application factory function.
      # blank line
    Args:  # Args:
        config_name: Configuration to use ('development', 'testing', 'production', 'default')  # config_name: Configuration to use ('development', 'testing', 'production', 'default')
        config_object: Optional configuration object to use directly (overrides config_name)  # config_object: Optional configuration object to use directly (overrides config_name)
      # blank line
    Returns:  # Returns:
        Flask application instance  # Flask application instance
    """  # """
    # Initialize Flask app instance  # # Initialize Flask app instance
    app = Flask(__name__)  # app = Flask(__name__)
      # blank line
    # Load configuration  # # Load configuration
    if config_object:  # if config_object:
        app.config.from_object(config_object)  # app.config.from_object(config_object)
    else:  # else:
        from config import config  # from config import config
        app.config.from_object(config[config_name])  # app.config.from_object(config[config_name])
      # blank line
    # Initialize database  # # Initialize database
    from app.models import db  # from app.models import db
    db.init_app(app)  # db.init_app(app)
      # blank line
    # Initialize Flask-Migrate with the app and database  # # Initialize Flask-Migrate with the app and database
    migrate.init_app(app, db)  # migrate.init_app(app, db)
      # blank line
    # Initialize Flask-Login  # # Initialize Flask-Login
    login_manager.init_app(app)  # login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'  # login_manager.login_message = 'Please log in to access this page.'
      # blank line
    # Initialize Flask-Mail  # # Initialize Flask-Mail
    mail.init_app(app)  # mail.init_app(app)
      # blank line
    # Initialize CORS for API endpoints  # # Initialize CORS for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # CORS(app, resources={r"/api/*": {"origins": "*"}})
      # blank line
    # User loader for Flask-Login  # # User loader for Flask-Login
    @login_manager.user_loader  # @login_manager.user_loader
    def load_user(user_id):  # def load_user(user_id):
        from app.models import User  # from app.models import User
        return User.query.get(int(user_id))  # return User.query.get(int(user_id))
      # blank line
    # Register blueprints  # # Register blueprints
    from app.routes import main  # from app.routes import main
    app.register_blueprint(main)  # app.register_blueprint(main)
      # blank line
    from app.auth import auth  # from app.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')  # app.register_blueprint(auth, url_prefix='/auth')
      # blank line
    # Initialize background scheduler  # # Initialize background scheduler
    from app.tasks import init_scheduler  # from app.tasks import init_scheduler
    init_scheduler(app)  # init_scheduler(app)
      # blank line
    # Create database tables if they don't exist  # # Create database tables if they don't exist
    with app.app_context():  # with app.app_context():
        db.create_all()  # db.create_all()
        # Create local server entry if it doesn't exist  # # Create local server entry if it doesn't exist
        from app.models import Server  # from app.models import Server
        local_server = Server.query.filter_by(is_local=True).first()  # local_server = Server.query.filter_by(is_local=True).first()
        if not local_server:  # if not local_server:
            import secrets  # import secrets
            local_server = Server(  # local_server = Server(
                name='Local Server',  # name='Local Server',
                hostname='localhost',  # hostname='localhost',
                api_key=secrets.token_urlsafe(32),  # api_key=secrets.token_urlsafe(32),
                is_local=True,  # is_local=True,
                is_active=True  # is_active=True
            )  # )
            db.session.add(local_server)  # db.session.add(local_server)
            db.session.commit()  # db.session.commit()
      # blank line
    return app  # return app
  # blank line
