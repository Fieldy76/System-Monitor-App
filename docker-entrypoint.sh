#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h "db" -U "$DB_USER" -d "system_monitor" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing migrations"
flask db upgrade

echo "Creating initial admin user if needed..."
python -c "
from app import create_app
from app.models import db, User, UserPreference
import os

app = create_app('production')
with app.app_context():
    # Check if any users exist
    if User.query.count() == 0:
        print('Creating initial admin user...')
        admin = User(
            username=os.environ.get('ADMIN_USERNAME', 'admin'),
            email=os.environ.get('ADMIN_EMAIL', 'admin@example.com'),
            is_admin=True
        )
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
        db.session.add(admin)
        db.session.commit()
        
        # Create preferences
        prefs = UserPreference(user_id=admin.id)
        db.session.add(prefs)
        db.session.commit()
        
        print(f'Admin user created: {admin.username}')
    else:
        print('Users already exist, skipping admin creation')
"

echo "Starting application..."
exec "$@"
