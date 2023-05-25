from unittest import TestCase
from models import User, db, bcrypt, connect_db
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_foodworx'
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_ECHO'] = False


class TestUserModel(TestCase):
    """Tests for User Model"""

    def setUp(self):
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()


    def test_user_registration(self):
        with app.app_context():
            user = User.register(first_name='new', last_name='test', username='test user', email='test@test.com', password='password')
            db.session.commit()
            self.assertEqual(user.username, 'test user')
            self.assertEqual(user.email, 'test@test.com')

    def test_password_hash(self):
        with app.app_context():

            user = User.register(first_name='new', last_name='test', username='test user', email='test@test.com', password='password')
            db.session.commit()
            self.assertTrue(User.authenticate_user('test user', 'password'))
            self.assertFalse(User.authenticate_user('test user', 'Password'))
    
    def test_user_authenticate(self):
        with app.app_context():
            user = User.register(first_name='new', last_name='test', username='test user', email='test@test.com', password='password')
            db.session.commit()
            u = User.authenticate_user('test user', 'password')
            self.assertTrue(u)
            self.assertEqual(user.username, 'test user')
            self.assertEqual(user.email, 'test@test.com')
            self.assertFalse(User.authenticate_user('test user', 'not-password'))
