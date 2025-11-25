# System Monitor App

A modern, real-time system monitoring web application built with Flask and Python. Monitor your system's CPU, memory, disk usage, and I/O statistics through a beautiful, responsive web interface with live updates and interactive charts.

![System Monitor](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Real-Time Monitoring
- **CPU Monitoring**: Track CPU usage percentage, frequency, and temperature (Celsius/Fahrenheit)
- **Memory Tracking**: Monitor RAM usage with total, used, and available memory statistics
- **Disk Usage**: View usage statistics for all mounted disk partitions
- **Disk I/O**: Track read/write operations and data transfer rates

### Modern User Interface
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Live Updates**: Real-time data refresh every second
- **Interactive Charts**: Visual representation of CPU and memory usage over time using Chart.js
- **Dark Mode**: Eye-friendly dark theme with glassmorphism effects
- **Smooth Animations**: Micro-animations and transitions for enhanced user experience

### Production Ready
- **Environment Configuration**: Separate configurations for development, testing, and production
- **Database Migration Support**: Flask-Migrate integration for future database features
- **Production Server**: Gunicorn WSGI server for production deployments
- **Security**: Environment-based secret key management
- **Testing**: Pytest integration for comprehensive testing

## 🖼️ Screenshots

> **Note**: The application features a premium dark mode interface with gradient accents, real-time charts, and smooth animations.

## 🛠️ Technology Stack

### Backend
- **Flask** - Lightweight WSGI web application framework
- **psutil** - Cross-platform library for system and process utilities
- **Flask-Migrate** - Database migration handling (SQLAlchemy integration)
- **Gunicorn** - Production-grade WSGI HTTP server
- **python-dotenv** - Environment variable management

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with custom properties, gradients, and animations
- **JavaScript (Vanilla)** - Real-time data fetching and DOM manipulation
- **Chart.js** - Interactive and responsive charts
- **Google Fonts (Outfit)** - Modern typography

### Development & Testing
- **pytest** - Testing framework
- **Git** - Version control

## 📁 Project Structure

```
System Monitor App/
├── app/                          # Application package
│   ├── __init__.py              # Application factory and initialization
│   ├── routes.py                # API routes and view logic
│   ├── models.py                # Database models (for future use)
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   │   └── style.css       # Application styles
│   │   └── js/
│   │       └── main.js         # Frontend JavaScript logic
│   └── templates/               # HTML templates
│       └── index.html          # Main application page
├── migrations/                   # Database migration files
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_routes.py          # Route tests
├── venv/                        # Virtual environment (not in git)
├── .env                         # Environment variables (not in git)
├── .gitignore                   # Git ignore rules
├── config.py                    # Configuration classes
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── DEPLOYMENT.md               # Production deployment guide
└── README.md                   # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "System Monitor App"
   ```

2. **Create a virtual environment**
   ```bash
   # On Linux/macOS
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   cp .env.example .env  # Or create manually
   
   # Edit .env and add:
   # FLASK_ENV=development
   # SECRET_KEY=your-secret-key-here
   ```

5. **Initialize database migrations (optional)**
   ```bash
   flask db init
   ```

## 💻 Usage

### Development Server

Run the application in development mode:

```bash
# Using Flask development server
flask run

# Or using the run.py script
python run.py
```

The application will be available at `http://localhost:5000`

### Production Server

For production deployment, use Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

## 🔌 API Endpoints

### GET `/`
Returns the main application page.

**Response**: HTML page

---

### GET `/api/metrics`
Returns real-time system metrics in JSON format.

**Response Example**:
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
    "available": "8.50GB",
    "used": "7.50GB",
    "percent": 46.9
  },
  "disk": [
    {
      "device": "/dev/sda1",
      "mountpoint": "/",
      "total": "500.00GB",
      "used": "250.00GB",
      "free": "250.00GB",
      "percent": 50.0
    }
  ],
  "io": {
    "read_bytes": "10.50GB",
    "write_bytes": "5.25GB",
    "read_count": 125000,
    "write_count": 75000
  }
}
```

**Update Frequency**: The frontend polls this endpoint every 1000ms (1 second)

## ⚙️ Configuration

The application supports three environment configurations:

### Development
- Debug mode enabled
- Auto-reload on code changes
- Detailed error pages
- Default SECRET_KEY (not secure)

### Testing
- Testing mode enabled
- Debug mode disabled
- Suitable for automated testing

### Production
- Debug mode disabled
- Requires SECRET_KEY environment variable
- Optimized for performance and security

### Environment Variables

Create a `.env` file in the project root:

```bash
# Environment (development, testing, production)
FLASK_ENV=development

# Secret key for session encryption (REQUIRED in production)
SECRET_KEY=your-very-secure-random-key-here

# Future database configuration
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

**Generate a secure SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🚢 Deployment

### Quick Deployment Options

#### Heroku
```bash
# Create Procfile
echo 'web: gunicorn "app:create_app(\"production\")"' > Procfile

# Deploy
heroku create your-app-name
git push heroku main
heroku config:set SECRET_KEY=your-secret-key
```

#### DigitalOcean / AWS / VPS
See the comprehensive [DEPLOYMENT.md](DEPLOYMENT.md) guide for:
- Gunicorn configuration
- Systemd service setup
- Nginx reverse proxy configuration
- SSL/TLS certificate setup
- Database migration workflows
- Security best practices

### Production Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Set secure `SECRET_KEY` environment variable
- [ ] Use Gunicorn (not Flask dev server)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Test on staging environment first

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_routes.py

# Run with coverage report
pytest --cov=app tests/
```

### Test Structure
```
tests/
├── __init__.py
└── test_routes.py    # Tests for routes and API endpoints
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Add tests for new features
   - Update documentation as needed
   - Follow existing code style
4. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Code Style Guidelines
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions and classes
- Keep functions focused and single-purpose

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **psutil** - For providing comprehensive system monitoring capabilities
- **Flask** - For the lightweight and flexible web framework
- **Chart.js** - For beautiful and responsive charts
- **Google Fonts** - For the Outfit font family

## 📞 Support

If you encounter any issues or have questions:

1. Check the [DEPLOYMENT.md](DEPLOYMENT.md) for deployment-related issues
2. Review existing issues in the repository
3. Open a new issue with detailed information about your problem

## 🔮 Future Enhancements

Planned features for future releases:

- [ ] Historical data storage with database integration
- [ ] Network monitoring (bandwidth, connections)
- [ ] Process monitoring and management
- [ ] Email/SMS alerts for threshold breaches
- [ ] Multi-server monitoring dashboard
- [ ] User authentication and authorization
- [ ] Customizable refresh intervals
- [ ] Export data to CSV/JSON
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests

---

**Built with ❤️ using Flask and Python**
