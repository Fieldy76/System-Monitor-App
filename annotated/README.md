# System Monitor App

A comprehensive, production-ready system monitoring web application built with Flask and Python. Monitor your systems in real-time with historical data storage, intelligent alerting, multi-server support, and enterprise-grade deployment options.

![System Monitor](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Architecture](#-architecture)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🔍 Real-Time System Monitoring
- **CPU Monitoring**: Track usage percentage, frequency, and temperature (Celsius/Fahrenheit)
- **Memory Tracking**: Monitor RAM usage with total, used, and available statistics
- **Disk Usage**: View usage statistics for all mounted partitions
- **Disk I/O**: Track read/write operations and data transfer rates
- **Network Monitoring**: Bandwidth usage, packet counts, and active connections
- **Live Updates**: Configurable refresh intervals (1s, 2s, 5s, 10s, 30s)

### 📊 Historical Data & Analytics
- **Database Integration**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **Metric Storage**: Automatic collection every 60 seconds
- **Data Retention**: Configurable retention policy (default: 30 days)
- **Historical Charts**: View trends over time (hours, days, weeks)
- **Data Export**: Export metrics to CSV or JSON with date range filtering

### ⚙️ Process Management
- **Process Monitoring**: View all running processes with PID, name, user, CPU%, memory%
- **Search & Filter**: Real-time process search functionality
- **Process Control**: Kill processes (admin only)
- **Auto-Refresh**: Live process list updates every 3 seconds
- **Process Details**: Detailed information for individual processes

### 🔔 Intelligent Alerting
- **Threshold Monitoring**: Configure alerts for CPU, memory, disk, temperature, network
- **Multiple Notification Channels**:
  - Email alerts via SMTP (Flask-Mail)
  - SMS alerts via Twilio
  - **Slack Notifications**: Rich alerts via Slack Webhooks
- **Flexible Rules**:
  - Comparison operators (>, <, >=, <=, ==)
  - Configurable thresholds
  - Duration settings (avoid false positives)
  - Per-server or global rules
- **Alert History**: Full logging with timestamps and acknowledgment tracking
- **Test Notifications**: Test email/SMS/Slack before activating rules

### 🏥 External Service Health Checks
- **Service Monitoring**: Monitor uptime and response time of external websites/APIs
- **Protocol Support**: HTTP/HTTPS and TCP checks
- **Status Dashboard**: Dedicated health dashboard with real-time status indicators
- **Performance Tracking**: Track response times and error rates
- **Background Monitoring**: Automated checks every 60 seconds

### 🖥️ Multi-Server Monitoring
- **Agent-Based Architecture**: Monitor multiple servers from one dashboard
- **Server Management**: Add, edit, and remove servers
- **Health Tracking**: Last seen timestamps and status indicators
- **API Key Authentication**: Secure server-to-server communication
- **Automatic Registration**: Local server auto-registered on first run

### 🔐 User Authentication & Authorization
- **Secure Authentication**: Flask-Login with bcrypt password hashing
- **User Management**:
  - Registration with validation
  - Login/logout functionality
  - Profile management (email, password changes)
- **Role-Based Access Control**:
  - Admin users (first user is auto-admin)
  - Regular users
  - Permission-based features (e.g., process killing)
- **Session Management**: Remember me functionality

### ⚡ Customizable Settings
- **User Preferences**:
  - Refresh interval configuration
  - Chart data points (30, 60, 120, 300)
  - Theme selection (dark, light, auto)
  - Default server selection
  - Notification preferences
- **Per-User Settings**: Each user maintains their own preferences

### 📦 Data Export
- **Multiple Formats**:
  - CSV export with human-readable formatting
  - JSON export with structured metadata
- **Flexible Filtering**:
  - Date range selection
  - Server filtering
  - Metric type selection (system, network, or both)
- **Automatic Downloads**: Proper MIME types and timestamped filenames

### 🐳 Docker & Kubernetes Ready
- **Docker Containerization**:
  - Multi-stage Dockerfile for optimized builds
  - Docker Compose for full stack (app + PostgreSQL + Redis)
  - Health checks and automatic restarts
  - Non-root user for security
- **Kubernetes Deployment**:
  - Complete manifest set (10 files)
  - StatefulSet for PostgreSQL with persistent storage
  - ConfigMap and Secret management
  - Horizontal scaling (2 app replicas)
  - Ingress with TLS support
  - Resource limits and requests
  - Liveness and readiness probes

### 🎨 Modern User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Eye-friendly with glassmorphism effects
- **Sidebar Navigation**: Easy access to all features
- **Interactive Charts**: Chart.js visualizations
- **Flash Messages**: User feedback with animations
- **Smooth Animations**: Micro-interactions for enhanced UX
- **Drag-and-Drop Dashboard**: Customizable widget layout using Gridstack.js
- **Widget Macros**: Reusable, modular dashboard components

## 🖼️ Screenshots

> **Note**: The application features a premium dark mode interface with gradient accents, real-time charts, and smooth animations.

## 🛠️ Technology Stack

### Backend
- **Flask 3.0+** - Web application framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-Mail** - Email notifications
- **Flask-Migrate** - Database migrations
- **psutil** - System and process utilities
- **APScheduler** - Background task scheduling
- **Gunicorn** - Production WSGI server
- **bcrypt** - Password hashing
- **Twilio** - SMS notifications
- **pandas** - Data export functionality

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with custom properties
- **JavaScript (Vanilla)** - Real-time updates and interactions
- **Chart.js** - Interactive charts
- **Google Fonts (Outfit)** - Typography

### Infrastructure
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **Redis** - Task queue backend
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **Nginx** - Reverse proxy (deployment)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd "System Monitor App"

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
docker-compose up -d

# Access the application
open http://localhost:5000
```

Default credentials (first user becomes admin):
- Create your account at `/auth/register`

### Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run migrations
flask db upgrade

# Start development server
python run.py
```

Access at `http://localhost:5000`

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 15+ (production) or SQLite (development)
- Redis 7+ (for background tasks)
- Node.js (optional, for frontend development)

### Detailed Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd "System Monitor App"
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your settings:
   ```bash
   # Flask Configuration
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   
   # Database (use PostgreSQL for production)
   DATABASE_URL=postgresql://user:password@localhost/system_monitor
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   
   # Email Alerts
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   
   # SMS Alerts (optional)
   TWILIO_ACCOUNT_SID=your-account-sid
   TWILIO_AUTH_TOKEN=your-auth-token
   TWILIO_PHONE_NUMBER=+1234567890
   
   # Monitoring Settings
   METRIC_COLLECTION_INTERVAL=60
   DATA_RETENTION_DAYS=30
   ```

3. **Initialize Database**
   ```bash
   flask db upgrade
   ```

4. **Run Application**
   ```bash
   # Development
   python run.py
   
   # Production
   gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Environment (development/production) | development | No |
| `SECRET_KEY` | Session encryption key | - | Yes (production) |
| `DATABASE_URL` | Database connection string | sqlite:///system_monitor.db | No |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 | No |
| `MAIL_SERVER` | SMTP server hostname | smtp.gmail.com | For alerts |
| `MAIL_PORT` | SMTP server port | 587 | For alerts |
| `MAIL_USERNAME` | Email account username | - | For alerts |
| `MAIL_PASSWORD` | Email account password | - | For alerts |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | - | For SMS |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | - | For SMS |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | - | For SMS |
| `METRIC_COLLECTION_INTERVAL` | Seconds between collections | 60 | No |
| `DATA_RETENTION_DAYS` | Days to keep metrics | 30 | No |
| `ALERT_CHECK_INTERVAL` | Seconds between alert checks | 60 | No |

### Generate Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate API key for servers
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🚢 Deployment

### Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Kubernetes Deployment

```bash
# Update secrets in k8s/secret.yaml first!

# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services

# Get external IP
kubectl get service system-monitor-service

# View logs
kubectl logs -f deployment/system-monitor-app

# Scale application
kubectl scale deployment system-monitor-app --replicas=3
```

### Production Checklist

- [x] Set `FLASK_ENV=production`
- [x] Configure secure `SECRET_KEY`
- [x] Use PostgreSQL database
- [x] Configure Redis for background tasks
- [x] Set up email/SMS credentials
- [x] Configure reverse proxy (Nginx)
- [x] Set up SSL/TLS certificates
- [x] Configure firewall rules
- [x] Set up monitoring and logging
- [x] Test on staging environment
- [x] Configure backup strategy
- [x] Set up log rotation

## 📚 API Documentation

### Authentication Endpoints

#### POST `/auth/register`
Register a new user account.

**Request Body**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "confirm_password": "securepassword123"
}
```

#### POST `/auth/login`
Authenticate user and create session.

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "securepassword123",
  "remember": true
}
```

### Metrics Endpoints

#### GET `/api/metrics?server_id=1`
Get real-time system metrics.

**Query Parameters**:
- `server_id` (optional): Server ID to query

**Response**:
```json
{
  "cpu": {
    "percent": 45.2,
    "freq": "2400.00Mhz",
    "temp_c": 55.0,
    "temp_f": 131.0
  },
  "memory": {
    "total": "16.00GB",
    "used": "7.50GB",
    "percent": 46.9
  },
  "network": {
    "bytes_sent": "1.50GB",
    "bytes_recv": "3.20GB",
    "packets_sent": 1500000,
    "packets_recv": 2000000
  },
  "connections": {
    "established": 45,
    "listen": 12,
    "time_wait": 8,
    "total": 65
  }
}
```

#### GET `/api/metrics/history?server_id=1&hours=24&type=system`
Get historical metrics data.

**Query Parameters**:
- `server_id` (optional): Server ID
- `hours` (default: 24): Hours of history
- `type` (default: system): Metric type (system/network)

### Process Endpoints

#### GET `/api/processes`
Get list of running processes.

**Response**:
```json
{
  "processes": [
    {
      "pid": 1234,
      "name": "python",
      "username": "user",
      "cpu_percent": 5.2,
      "memory_percent": 2.1,
      "status": "running"
    }
  ]
}
```

#### POST `/api/processes/<pid>/kill`
Terminate a process (admin only).

### Alert Endpoints

#### GET `/api/alerts/rules`
Get all alert rules for current user.

#### POST `/api/alerts/rules`
Create new alert rule.

**Request Body**:
```json
{
  "name": "High CPU Alert",
  "metric_type": "cpu",
  "threshold": 80,
  "comparison": ">",
  "server_id": null,
  "notify_email": true,
  "notify_sms": false,
  "email_address": "alerts@example.com"
}
```

#### GET `/api/alerts/history?limit=50`
Get alert history.

### Export Endpoints

#### GET `/api/export/csv?server_id=1&days=7&metrics=system,network`
Export metrics to CSV.

#### GET `/api/export/json?server_id=1&days=7&metrics=system,network`
Export metrics to JSON.

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Nginx (Proxy)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│  Flask App      │────▶│  PostgreSQL  │
│  (Gunicorn)     │     │  Database    │
└────────┬────────┘     └──────────────┘
         │
         │              ┌──────────────┐
         └─────────────▶│    Redis     │
                        │  Task Queue  │
                        └──────────────┘
```

### Background Tasks

- **Metric Collection**: Runs every 60 seconds (configurable)
- **Alert Checking**: Runs every 60 seconds (configurable)
- **Data Cleanup**: Runs daily at 2 AM

### Database Schema

```
users
├── id (PK)
├── username (unique)
├── email (unique)
├── password_hash
├── is_admin
└── created_at

servers
├── id (PK)
├── name
├── hostname
├── api_key
├── is_local
└── is_active

system_metrics
├── id (PK)
├── server_id (FK)
├── timestamp
├── cpu_percent
├── memory_percent
└── ...

alert_rules
├── id (PK)
├── user_id (FK)
├── server_id (FK, nullable)
├── metric_type
├── threshold
└── ...
```

## 🧪 Testing

The application includes a suite of unit and integration tests.

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_models.py
python -m unittest tests/test_routes.py

# Run with verbose output
python -m unittest discover tests -v
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Add docstrings to functions and classes
- Write tests for new features
- Update documentation as needed
- Keep commits focused and atomic

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **psutil** - System monitoring capabilities
- **Flask** - Web framework
- **Chart.js** - Data visualization
- **SQLAlchemy** - Database ORM
- **APScheduler** - Background task scheduling

## 📞 Support

For issues and questions:

1. Check existing documentation
2. Review [GitHub Issues](https://github.com/your-repo/issues)
3. Open a new issue with detailed information

## 🔗 Related Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [API Documentation](docs/API.md) - Complete API reference
- [Agent Setup](docs/AGENT_SETUP.md) - Multi-server agent configuration

---

**Built with ❤️ using Flask, Python, and modern web technologies**

**Status**: ✅ Production Ready | 🐳 Docker Ready | ☸️ Kubernetes Ready
