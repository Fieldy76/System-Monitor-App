"""Database models for system monitoring application."""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy instance
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    alert_rules = db.relationship('AlertRule', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Server(db.Model):
    """Server model for multi-server monitoring."""
    __tablename__ = 'servers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_local = db.Column(db.Boolean, default=False)  # True for the local server
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    system_metrics = db.relationship('SystemMetric', backref='server', cascade='all, delete-orphan')
    network_metrics = db.relationship('NetworkMetric', backref='server', cascade='all, delete-orphan')
    process_snapshots = db.relationship('ProcessSnapshot', backref='server', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Server {self.name}>'


class SystemMetric(db.Model):
    """System metrics model for historical data storage."""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # CPU metrics
    cpu_percent = db.Column(db.Float, nullable=False)
    cpu_freq = db.Column(db.Float)  # MHz
    cpu_temp_c = db.Column(db.Float)  # Celsius
    
    # Memory metrics
    memory_total = db.Column(db.BigInteger, nullable=False)  # bytes
    memory_used = db.Column(db.BigInteger, nullable=False)  # bytes
    memory_percent = db.Column(db.Float, nullable=False)
    
    # Disk metrics
    disk_total = db.Column(db.BigInteger)  # bytes
    disk_used = db.Column(db.BigInteger)  # bytes
    disk_percent = db.Column(db.Float)
    
    # I/O metrics
    io_read_bytes = db.Column(db.BigInteger)
    io_write_bytes = db.Column(db.BigInteger)
    io_read_count = db.Column(db.Integer)
    io_write_count = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<SystemMetric server={self.server_id} time={self.timestamp}>'


class NetworkMetric(db.Model):
    """Network metrics model for bandwidth and connection tracking."""
    __tablename__ = 'network_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Network I/O
    bytes_sent = db.Column(db.BigInteger, nullable=False)
    bytes_recv = db.Column(db.BigInteger, nullable=False)
    packets_sent = db.Column(db.BigInteger)
    packets_recv = db.Column(db.BigInteger)
    
    # Connections
    connections_established = db.Column(db.Integer)
    connections_listen = db.Column(db.Integer)
    connections_time_wait = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<NetworkMetric server={self.server_id} time={self.timestamp}>'


class ProcessSnapshot(db.Model):
    """Process snapshot model for process monitoring."""
    __tablename__ = 'process_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    pid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100))
    cpu_percent = db.Column(db.Float)
    memory_percent = db.Column(db.Float)
    status = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<ProcessSnapshot pid={self.pid} name={self.name}>'


class AlertRule(db.Model):
    """Alert rule model for threshold-based alerts."""
    __tablename__ = 'alert_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))  # None = all servers
    
    name = db.Column(db.String(100), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # cpu, memory, disk, network
    threshold = db.Column(db.Float, nullable=False)
    comparison = db.Column(db.String(10), nullable=False)  # >, <, >=, <=, ==
    duration = db.Column(db.Integer, default=60)  # seconds the condition must persist
    
    # Notification settings
    notify_email = db.Column(db.Boolean, default=True)
    notify_sms = db.Column(db.Boolean, default=False)
    notify_slack = db.Column(db.Boolean, default=False)
    email_address = db.Column(db.String(120))  # Override user's email
    phone_number = db.Column(db.String(20))  # For SMS
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    alert_history = db.relationship('AlertHistory', backref='rule', cascade='all, delete-orphan')
    # user relationship is defined in User model with backref='alert_rules'
    server = db.relationship('Server', backref=db.backref('alert_rules', lazy=True))
    
    def __repr__(self):
        return f'<AlertRule {self.name}>'


class AlertHistory(db.Model):
    """Alert history model for tracking triggered alerts."""
    __tablename__ = 'alert_history'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'), nullable=False, index=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    
    triggered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    metric_value = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    
    # Notification status
    email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)
    slack_sent = db.Column(db.Boolean, default=False)
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<AlertHistory rule={self.rule_id} time={self.triggered_at}>'


class UserPreference(db.Model):
    """User preferences model for customizable settings."""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Dashboard settings
    refresh_interval = db.Column(db.Integer, default=1000)  # milliseconds
    chart_data_points = db.Column(db.Integer, default=60)
    theme = db.Column(db.String(20), default='dark')  # dark, light, auto
    
    # Default server
    default_server_id = db.Column(db.Integer, db.ForeignKey('servers.id'))
    
    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<UserPreference user={self.user_id}>'

    def to_dict(self):
        """Convert preferences to dictionary."""
        return {
            'refresh_interval': self.refresh_interval,
            'chart_data_points': self.chart_data_points,
            'theme': self.theme,
            'default_server_id': self.default_server_id,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications
        }


class ServiceHealth(db.Model):
    """Model for monitoring external services and microservices."""
    __tablename__ = 'service_health'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    check_interval = db.Column(db.Integer, default=60)  # seconds
    timeout = db.Column(db.Integer, default=5)  # seconds
    is_active = db.Column(db.Boolean, default=True)
    
    # Health status
    last_check_time = db.Column(db.DateTime)
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # milliseconds
    is_up = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<ServiceHealth {self.name}>'
    
    def to_dict(self):
        """Convert service health to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'check_interval': self.check_interval,
            'timeout': self.timeout,
            'is_active': self.is_active,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'is_up': self.is_up,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DashboardLayout(db.Model):
    """Model for storing user's customizable dashboard layouts."""
    __tablename__ = 'dashboard_layouts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), default='Default Layout')
    layout_config = db.Column(db.JSON)  # Stores widget positions and sizes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user = db.relationship('User', backref=db.backref('dashboard_layouts', lazy=True))
    
    def __repr__(self):
        return f'<DashboardLayout {self.name} (User: {self.user_id})>'
    
    def to_dict(self):
        """Convert layout to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'layout_config': self.layout_config,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
