import unittest
from app import create_app
from app.models import db, User, Server, ServiceHealth, AlertRule
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_object=TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan', email='susan@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_service_health_model(self):
        s = ServiceHealth(name='Google', url='https://google.com')
        db.session.add(s)
        db.session.commit()
        self.assertEqual(s.check_interval, 60)
        self.assertTrue(s.is_active)

    def test_alert_rule_model(self):
        u = User(username='john', email='john@example.com')
        u.set_password('123')
        db.session.add(u)
        db.session.commit()
        
        rule = AlertRule(
            user_id=u.id,
            name='High CPU',
            metric_type='cpu',
            threshold=90,
            comparison='>',
            notify_slack=True
        )
        db.session.add(rule)
        db.session.commit()
        
        self.assertTrue(rule.notify_slack)
        self.assertEqual(rule.metric_type, 'cpu')

if __name__ == '__main__':
    unittest.main(verbosity=2)
