import unittest  # import unittest
import json  # import json
from app import create_app  # from app import create_app
from app.models import db, User, ServiceHealth  # from app.models import db, User, ServiceHealth
from config import Config  # from config import Config
  # blank line
class TestConfig(Config):  # class TestConfig(Config):
    TESTING = True  # TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # WTF_CSRF_ENABLED = False
  # blank line
class RoutesTestCase(unittest.TestCase):  # class RoutesTestCase(unittest.TestCase):
    def setUp(self):  # def setUp(self):
        self.app = create_app(config_object=TestConfig)  # self.app = create_app(config_object=TestConfig)
        self.app_context = self.app.app_context()  # self.app_context = self.app.app_context()
        self.app_context.push()  # self.app_context.push()
        db.create_all()  # db.create_all()
        self.client = self.app.test_client()  # self.client = self.app.test_client()
          # blank line
        # Create admin user  # # Create admin user
        u = User(username='admin', email='admin@example.com', is_admin=True)  # u = User(username='admin', email='admin@example.com', is_admin=True)
        u.set_password('admin')  # u.set_password('admin')
        db.session.add(u)  # db.session.add(u)
        db.session.commit()  # db.session.commit()
  # blank line
    def tearDown(self):  # def tearDown(self):
        db.session.remove()  # db.session.remove()
        db.drop_all()  # db.drop_all()
        self.app_context.pop()  # self.app_context.pop()
  # blank line
    def login(self, username, password):  # def login(self, username, password):
        return self.client.post('/auth/login', data=dict(  # return self.client.post('/auth/login', data=dict(
            username=username,  # username=username,
            password=password  # password=password
        ), follow_redirects=True)  # ), follow_redirects=True)
  # blank line
    def test_health_check_endpoint(self):  # def test_health_check_endpoint(self):
        self.login('admin', 'admin')  # self.login('admin', 'admin')
          # blank line
        # Create a service  # # Create a service
        response = self.client.post('/api/health/services', json={  # response = self.client.post('/api/health/services', json={
            'name': 'Test Service',  # 'name': 'Test Service',
            'url': 'https://example.com'  # 'url': 'https://example.com'
        })  # })
        self.assertEqual(response.status_code, 201)  # self.assertEqual(response.status_code, 201)
          # blank line
        # Get services  # # Get services
        response = self.client.get('/api/health/services')  # response = self.client.get('/api/health/services')
        self.assertEqual(response.status_code, 200)  # self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)  # data = json.loads(response.data)
        self.assertEqual(len(data['services']), 1)  # self.assertEqual(len(data['services']), 1)
        self.assertEqual(data['services'][0]['name'], 'Test Service')  # self.assertEqual(data['services'][0]['name'], 'Test Service')
  # blank line
    def test_metrics_endpoint(self):  # def test_metrics_endpoint(self):
        self.login('admin', 'admin')  # self.login('admin', 'admin')
        response = self.client.get('/api/metrics')  # response = self.client.get('/api/metrics')
        self.assertEqual(response.status_code, 200)  # self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)  # data = json.loads(response.data)
        self.assertIn('cpu', data)  # self.assertIn('cpu', data)
        self.assertIn('memory', data)  # self.assertIn('memory', data)
  # blank line
if __name__ == '__main__':  # if __name__ == '__main__':
    unittest.main(verbosity=2)  # unittest.main(verbosity=2)
