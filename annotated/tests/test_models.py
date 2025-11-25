import unittest  # import unittest
from app import create_app  # from app import create_app
from app.models import db, User, Server, ServiceHealth, AlertRule  # from app.models import db, User, Server, ServiceHealth, AlertRule
from config import Config  # from config import Config
  # blank line
class TestConfig(Config):  # class TestConfig(Config):
    TESTING = True  # TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # WTF_CSRF_ENABLED = False
  # blank line
class UserModelCase(unittest.TestCase):  # class UserModelCase(unittest.TestCase):
    def setUp(self):  # def setUp(self):
        self.app = create_app(config_object=TestConfig)  # self.app = create_app(config_object=TestConfig)
        self.app_context = self.app.app_context()  # self.app_context = self.app.app_context()
        self.app_context.push()  # self.app_context.push()
        db.create_all()  # db.create_all()
  # blank line
    def tearDown(self):  # def tearDown(self):
        db.session.remove()  # db.session.remove()
        db.drop_all()  # db.drop_all()
        self.app_context.pop()  # self.app_context.pop()
  # blank line
    def test_password_hashing(self):  # def test_password_hashing(self):
        u = User(username='susan', email='susan@example.com')  # u = User(username='susan', email='susan@example.com')
        u.set_password('cat')  # u.set_password('cat')
        self.assertFalse(u.check_password('dog'))  # self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))  # self.assertTrue(u.check_password('cat'))
  # blank line
    def test_service_health_model(self):  # def test_service_health_model(self):
        s = ServiceHealth(name='Google', url='https://google.com')  # s = ServiceHealth(name='Google', url='https://google.com')
        db.session.add(s)  # db.session.add(s)
        db.session.commit()  # db.session.commit()
        self.assertEqual(s.check_interval, 60)  # self.assertEqual(s.check_interval, 60)
        self.assertTrue(s.is_active)  # self.assertTrue(s.is_active)
  # blank line
    def test_alert_rule_model(self):  # def test_alert_rule_model(self):
        u = User(username='john', email='john@example.com')  # u = User(username='john', email='john@example.com')
        u.set_password('123')  # u.set_password('123')
        db.session.add(u)  # db.session.add(u)
        db.session.commit()  # db.session.commit()
          # blank line
        rule = AlertRule(  # rule = AlertRule(
            user_id=u.id,  # user_id=u.id,
            name='High CPU',  # name='High CPU',
            metric_type='cpu',  # metric_type='cpu',
            threshold=90,  # threshold=90,
            comparison='>',  # comparison='>',
            notify_slack=True  # notify_slack=True
        )  # )
        db.session.add(rule)  # db.session.add(rule)
        db.session.commit()  # db.session.commit()
          # blank line
        self.assertTrue(rule.notify_slack)  # self.assertTrue(rule.notify_slack)
        self.assertEqual(rule.metric_type, 'cpu')  # self.assertEqual(rule.metric_type, 'cpu')
  # blank line
if __name__ == '__main__':  # if __name__ == '__main__':
    unittest.main(verbosity=2)  # unittest.main(verbosity=2)
