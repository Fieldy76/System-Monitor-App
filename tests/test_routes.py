import unittest
import json
from app import create_app
from app.models import db, User, ServiceHealth
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_object=TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create admin user
        u = User(username='admin', email='admin@example.com', is_admin=True)
        u.set_password('admin')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.client.post('/auth/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_health_check_endpoint(self):
        self.login('admin', 'admin')
        
        # Create a service
        response = self.client.post('/api/health/services', json={
            'name': 'Test Service',
            'url': 'https://example.com'
        })
        self.assertEqual(response.status_code, 201)
        
        # Get services
        response = self.client.get('/api/health/services')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['services']), 1)
        self.assertEqual(data['services'][0]['name'], 'Test Service')

    def test_metrics_endpoint(self):
        self.login('admin', 'admin')
        response = self.client.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('cpu', data)
        self.assertIn('memory', data)

if __name__ == '__main__':
    unittest.main(verbosity=2)
