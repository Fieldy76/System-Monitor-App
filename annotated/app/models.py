"""Database models for system monitoring application."""  # """Database models for system monitoring application."""
from datetime import datetime  # from datetime import datetime
from flask_sqlalchemy import SQLAlchemy  # from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin  # from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # from werkzeug.security import generate_password_hash, check_password_hash
  # blank line
# Initialize SQLAlchemy instance  # # Initialize SQLAlchemy instance
db = SQLAlchemy()  # db = SQLAlchemy()
  # blank line
  # blank line
class User(UserMixin, db.Model):  # class User(UserMixin, db.Model):
    """User model for authentication and authorization."""  # """User model for authentication and authorization."""
    __tablename__ = 'users'  # __tablename__ = 'users'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)  # username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)  # email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)  # last_login = db.Column(db.DateTime)
      # blank line
    # Relationships  # # Relationships
    preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')  # preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    alert_rules = db.relationship('AlertRule', backref='user', cascade='all, delete-orphan')  # alert_rules = db.relationship('AlertRule', backref='user', cascade='all, delete-orphan')
      # blank line
    def set_password(self, password):  # def set_password(self, password):
        """Hash and set the user's password."""  # """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)  # self.password_hash = generate_password_hash(password)
      # blank line
    def check_password(self, password):  # def check_password(self, password):
        """Check if the provided password matches the hash."""  # """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)  # return check_password_hash(self.password_hash, password)
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<User {self.username}>'  # return f'<User {self.username}>'
  # blank line
  # blank line
class Server(db.Model):  # class Server(db.Model):
    """Server model for multi-server monitoring."""  # """Server model for multi-server monitoring."""
    __tablename__ = 'servers'  # __tablename__ = 'servers'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # name = db.Column(db.String(100), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)  # hostname = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)  # api_key = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # is_active = db.Column(db.Boolean, default=True)
    is_local = db.Column(db.Boolean, default=False)  # True for the local server  # is_local = db.Column(db.Boolean, default=False)  # True for the local server
    last_seen = db.Column(db.DateTime)  # last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # created_at = db.Column(db.DateTime, default=datetime.utcnow)
      # blank line
    # Relationships  # # Relationships
    system_metrics = db.relationship('SystemMetric', backref='server', cascade='all, delete-orphan')  # system_metrics = db.relationship('SystemMetric', backref='server', cascade='all, delete-orphan')
    network_metrics = db.relationship('NetworkMetric', backref='server', cascade='all, delete-orphan')  # network_metrics = db.relationship('NetworkMetric', backref='server', cascade='all, delete-orphan')
    process_snapshots = db.relationship('ProcessSnapshot', backref='server', cascade='all, delete-orphan')  # process_snapshots = db.relationship('ProcessSnapshot', backref='server', cascade='all, delete-orphan')
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<Server {self.name}>'  # return f'<Server {self.name}>'
  # blank line
  # blank line
class SystemMetric(db.Model):  # class SystemMetric(db.Model):
    """System metrics model for historical data storage."""  # """System metrics model for historical data storage."""
    __tablename__ = 'system_metrics'  # __tablename__ = 'system_metrics'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)  # server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
      # blank line
    # CPU metrics  # # CPU metrics
    cpu_percent = db.Column(db.Float, nullable=False)  # cpu_percent = db.Column(db.Float, nullable=False)
    cpu_freq = db.Column(db.Float)  # MHz  # cpu_freq = db.Column(db.Float)  # MHz
    cpu_temp_c = db.Column(db.Float)  # Celsius  # cpu_temp_c = db.Column(db.Float)  # Celsius
      # blank line
    # Memory metrics  # # Memory metrics
    memory_total = db.Column(db.BigInteger, nullable=False)  # bytes  # memory_total = db.Column(db.BigInteger, nullable=False)  # bytes
    memory_used = db.Column(db.BigInteger, nullable=False)  # bytes  # memory_used = db.Column(db.BigInteger, nullable=False)  # bytes
    memory_percent = db.Column(db.Float, nullable=False)  # memory_percent = db.Column(db.Float, nullable=False)
      # blank line
    # Disk metrics  # # Disk metrics
    disk_total = db.Column(db.BigInteger)  # bytes  # disk_total = db.Column(db.BigInteger)  # bytes
    disk_used = db.Column(db.BigInteger)  # bytes  # disk_used = db.Column(db.BigInteger)  # bytes
    disk_percent = db.Column(db.Float)  # disk_percent = db.Column(db.Float)
      # blank line
    # I/O metrics  # # I/O metrics
    io_read_bytes = db.Column(db.BigInteger)  # io_read_bytes = db.Column(db.BigInteger)
    io_write_bytes = db.Column(db.BigInteger)  # io_write_bytes = db.Column(db.BigInteger)
    io_read_count = db.Column(db.Integer)  # io_read_count = db.Column(db.Integer)
    io_write_count = db.Column(db.Integer)  # io_write_count = db.Column(db.Integer)
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<SystemMetric server={self.server_id} time={self.timestamp}>'  # return f'<SystemMetric server={self.server_id} time={self.timestamp}>'
  # blank line
  # blank line
class NetworkMetric(db.Model):  # class NetworkMetric(db.Model):
    """Network metrics model for bandwidth and connection tracking."""  # """Network metrics model for bandwidth and connection tracking."""
    __tablename__ = 'network_metrics'  # __tablename__ = 'network_metrics'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)  # server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
      # blank line
    # Network I/O  # # Network I/O
    bytes_sent = db.Column(db.BigInteger, nullable=False)  # bytes_sent = db.Column(db.BigInteger, nullable=False)
    bytes_recv = db.Column(db.BigInteger, nullable=False)  # bytes_recv = db.Column(db.BigInteger, nullable=False)
    packets_sent = db.Column(db.BigInteger)  # packets_sent = db.Column(db.BigInteger)
    packets_recv = db.Column(db.BigInteger)  # packets_recv = db.Column(db.BigInteger)
      # blank line
    # Connections  # # Connections
    connections_established = db.Column(db.Integer)  # connections_established = db.Column(db.Integer)
    connections_listen = db.Column(db.Integer)  # connections_listen = db.Column(db.Integer)
    connections_time_wait = db.Column(db.Integer)  # connections_time_wait = db.Column(db.Integer)
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<NetworkMetric server={self.server_id} time={self.timestamp}>'  # return f'<NetworkMetric server={self.server_id} time={self.timestamp}>'
  # blank line
  # blank line
class ProcessSnapshot(db.Model):  # class ProcessSnapshot(db.Model):
    """Process snapshot model for process monitoring."""  # """Process snapshot model for process monitoring."""
    __tablename__ = 'process_snapshots'  # __tablename__ = 'process_snapshots'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)  # server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
      # blank line
    pid = db.Column(db.Integer, nullable=False)  # pid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)  # name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100))  # username = db.Column(db.String(100))
    cpu_percent = db.Column(db.Float)  # cpu_percent = db.Column(db.Float)
    memory_percent = db.Column(db.Float)  # memory_percent = db.Column(db.Float)
    status = db.Column(db.String(50))  # status = db.Column(db.String(50))
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<ProcessSnapshot pid={self.pid} name={self.name}>'  # return f'<ProcessSnapshot pid={self.pid} name={self.name}>'
  # blank line
  # blank line
class AlertRule(db.Model):  # class AlertRule(db.Model):
    """Alert rule model for threshold-based alerts."""  # """Alert rule model for threshold-based alerts."""
    __tablename__ = 'alert_rules'  # __tablename__ = 'alert_rules'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))  # None = all servers  # server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))  # None = all servers
      # blank line
    name = db.Column(db.String(100), nullable=False)  # name = db.Column(db.String(100), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # cpu, memory, disk, network  # metric_type = db.Column(db.String(50), nullable=False)  # cpu, memory, disk, network
    threshold = db.Column(db.Float, nullable=False)  # threshold = db.Column(db.Float, nullable=False)
    comparison = db.Column(db.String(10), nullable=False)  # >, <, >=, <=, ==  # comparison = db.Column(db.String(10), nullable=False)  # >, <, >=, <=, ==
    duration = db.Column(db.Integer, default=60)  # seconds the condition must persist  # duration = db.Column(db.Integer, default=60)  # seconds the condition must persist
      # blank line
    # Notification settings  # # Notification settings
    notify_email = db.Column(db.Boolean, default=True)  # notify_email = db.Column(db.Boolean, default=True)
    notify_sms = db.Column(db.Boolean, default=False)  # notify_sms = db.Column(db.Boolean, default=False)
    notify_slack = db.Column(db.Boolean, default=False)  # notify_slack = db.Column(db.Boolean, default=False)
    email_address = db.Column(db.String(120))  # Override user's email  # email_address = db.Column(db.String(120))  # Override user's email
    phone_number = db.Column(db.String(20))  # For SMS  # phone_number = db.Column(db.String(20))  # For SMS
      # blank line
    is_active = db.Column(db.Boolean, default=True)  # is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
      # blank line
    # Relationships  # # Relationships
    alert_history = db.relationship('AlertHistory', backref='rule', cascade='all, delete-orphan')  # alert_history = db.relationship('AlertHistory', backref='rule', cascade='all, delete-orphan')
    # user relationship is defined in User model with backref='alert_rules'  # # user relationship is defined in User model with backref='alert_rules'
    server = db.relationship('Server', backref=db.backref('alert_rules', lazy=True))  # server = db.relationship('Server', backref=db.backref('alert_rules', lazy=True))
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<AlertRule {self.name}>'  # return f'<AlertRule {self.name}>'
  # blank line
  # blank line
class AlertHistory(db.Model):  # class AlertHistory(db.Model):
    """Alert history model for tracking triggered alerts."""  # """Alert history model for tracking triggered alerts."""
    __tablename__ = 'alert_history'  # __tablename__ = 'alert_history'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'), nullable=False, index=True)  # rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'), nullable=False, index=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)  # server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
      # blank line
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # triggered_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    metric_value = db.Column(db.Float, nullable=False)  # metric_value = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)  # message = db.Column(db.Text)
      # blank line
    # Notification status  # # Notification status
    email_sent = db.Column(db.Boolean, default=False)  # email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)  # sms_sent = db.Column(db.Boolean, default=False)
    slack_sent = db.Column(db.Boolean, default=False)  # slack_sent = db.Column(db.Boolean, default=False)
    acknowledged = db.Column(db.Boolean, default=False)  # acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)  # acknowledged_at = db.Column(db.DateTime)
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<AlertHistory rule={self.rule_id} time={self.triggered_at}>'  # return f'<AlertHistory rule={self.rule_id} time={self.triggered_at}>'
  # blank line
  # blank line
class UserPreference(db.Model):  # class UserPreference(db.Model):
    """User preferences model for customizable settings."""  # """User preferences model for customizable settings."""
    __tablename__ = 'user_preferences'  # __tablename__ = 'user_preferences'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)  # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
      # blank line
    # Dashboard settings  # # Dashboard settings
    refresh_interval = db.Column(db.Integer, default=1000)  # milliseconds  # refresh_interval = db.Column(db.Integer, default=1000)  # milliseconds
    chart_data_points = db.Column(db.Integer, default=60)  # chart_data_points = db.Column(db.Integer, default=60)
    theme = db.Column(db.String(20), default='dark')  # dark, light, auto  # theme = db.Column(db.String(20), default='dark')  # dark, light, auto
      # blank line
    # Default server  # # Default server
    default_server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))  # default_server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
      # blank line
    # Notification preferences  # # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True)  # email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)  # sms_notifications = db.Column(db.Boolean, default=False)
      # blank line
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<UserPreference user={self.user_id}>'  # return f'<UserPreference user={self.user_id}>'
  # blank line
    def to_dict(self):  # def to_dict(self):
        """Convert preferences to dictionary."""  # """Convert preferences to dictionary."""
        return {  # return {
            'refresh_interval': self.refresh_interval,  # 'refresh_interval': self.refresh_interval,
            'chart_data_points': self.chart_data_points,  # 'chart_data_points': self.chart_data_points,
            'theme': self.theme,  # 'theme': self.theme,
            'default_server_id': self.default_server_id,  # 'default_server_id': self.default_server_id,
            'email_notifications': self.email_notifications,  # 'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications  # 'sms_notifications': self.sms_notifications
        }  # }
  # blank line
  # blank line
class ServiceHealth(db.Model):  # class ServiceHealth(db.Model):
    """Model for monitoring external services and microservices."""  # """Model for monitoring external services and microservices."""
    __tablename__ = 'service_health'  # __tablename__ = 'service_health'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)  # url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)  # description = db.Column(db.Text)
    check_interval = db.Column(db.Integer, default=60)  # seconds  # check_interval = db.Column(db.Integer, default=60)  # seconds
    timeout = db.Column(db.Integer, default=5)  # seconds  # timeout = db.Column(db.Integer, default=5)  # seconds
    is_active = db.Column(db.Boolean, default=True)  # is_active = db.Column(db.Boolean, default=True)
      # blank line
    # Health status  # # Health status
    last_check_time = db.Column(db.DateTime)  # last_check_time = db.Column(db.DateTime)
    status_code = db.Column(db.Integer)  # status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # milliseconds  # response_time = db.Column(db.Float)  # milliseconds
    is_up = db.Column(db.Boolean, default=True)  # is_up = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)  # error_message = db.Column(db.Text)
      # blank line
    # Metadata  # # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<ServiceHealth {self.name}>'  # return f'<ServiceHealth {self.name}>'
      # blank line
    def to_dict(self):  # def to_dict(self):
        """Convert service health to dictionary."""  # """Convert service health to dictionary."""
        return {  # return {
            'id': self.id,  # 'id': self.id,
            'name': self.name,  # 'name': self.name,
            'url': self.url,  # 'url': self.url,
            'description': self.description,  # 'description': self.description,
            'check_interval': self.check_interval,  # 'check_interval': self.check_interval,
            'timeout': self.timeout,  # 'timeout': self.timeout,
            'is_active': self.is_active,  # 'is_active': self.is_active,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,  # 'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'status_code': self.status_code,  # 'status_code': self.status_code,
            'response_time': self.response_time,  # 'response_time': self.response_time,
            'is_up': self.is_up,  # 'is_up': self.is_up,
            'error_message': self.error_message,  # 'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None  # 'created_at': self.created_at.isoformat() if self.created_at else None
        }  # }
  # blank line
  # blank line
class DashboardLayout(db.Model):  # class DashboardLayout(db.Model):
    """Model for storing user's customizable dashboard layouts."""  # """Model for storing user's customizable dashboard layouts."""
    __tablename__ = 'dashboard_layouts'  # __tablename__ = 'dashboard_layouts'
      # blank line
    id = db.Column(db.Integer, primary_key=True)  # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), default='Default Layout')  # name = db.Column(db.String(100), default='Default Layout')
    layout_config = db.Column(db.JSON)  # Stores widget positions and sizes  # layout_config = db.Column(db.JSON)  # Stores widget positions and sizes
    is_active = db.Column(db.Boolean, default=True)  # is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
      # blank line
    # Relationship  # # Relationship
    user = db.relationship('User', backref=db.backref('dashboard_layouts', lazy=True))  # user = db.relationship('User', backref=db.backref('dashboard_layouts', lazy=True))
      # blank line
    def __repr__(self):  # def __repr__(self):
        return f'<DashboardLayout {self.name} (User: {self.user_id})>'  # return f'<DashboardLayout {self.name} (User: {self.user_id})>'
      # blank line
    def to_dict(self):  # def to_dict(self):
        """Convert layout to dictionary."""  # """Convert layout to dictionary."""
        return {  # return {
            'id': self.id,  # 'id': self.id,
            'user_id': self.user_id,  # 'user_id': self.user_id,
            'name': self.name,  # 'name': self.name,
            'layout_config': self.layout_config,  # 'layout_config': self.layout_config,
            'is_active': self.is_active,  # 'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,  # 'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None  # 'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }  # }
