# Production Deployment Guide

## Running with Gunicorn (Production Server)

### Basic Command
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Recommended Production Command
```bash
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  "app:create_app('production')"
```

### Options Explained
- `--workers 4`: Number of worker processes (typically 2-4 × CPU cores)
- `--bind 0.0.0.0:5000`: Listen on all interfaces, port 5000
- `--timeout 120`: Worker timeout in seconds
- `--access-logfile -`: Log access to stdout
- `--error-logfile -`: Log errors to stdout
- `"app:create_app('production')"`: Application factory with production config

## Database Migrations (Flask-Migrate)

### Initialize Migrations (First Time Only)
```bash
flask db init
```

### Create a Migration
```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations
```bash
flask db upgrade
```

### Rollback Migration
```bash
flask db downgrade
```

## Environment Variables

Set these in your production environment:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-very-secure-random-key-here
# Add database URL when you add a database
# export DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Deployment Checklist

- [ ] Set `SECRET_KEY` environment variable
- [ ] Set `FLASK_ENV=production`
- [ ] Run with Gunicorn (not Flask dev server)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Configure database backups (when using a database)
- [ ] Test migrations on staging environment first

## Common Deployment Platforms

### Heroku
```bash
# Procfile
web: gunicorn "app:create_app('production')"
```

### AWS/DigitalOcean/VPS
Use systemd service file:
```ini
[Unit]
Description=System Monitor App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app('production')"

[Install]
WantedBy=multi-user.target
```

## Security Notes

1. **Never commit `.env` file** - It's in `.gitignore` for a reason
2. **Use strong SECRET_KEY** - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
3. **Use HTTPS in production** - Set up SSL/TLS certificates
4. **Keep dependencies updated** - Run `pip list --outdated` regularly
5. **Use environment variables** - Never hardcode secrets in code
