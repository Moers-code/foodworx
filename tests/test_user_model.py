from unittest import TestCase
from flask import Flask
from models import User, connect_db, db


class UserTestCase(TestCase):
    
    def setUp(self):
        # Create a test Flask app
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///foodworx-test'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True

        # Connect the database to the Flask app if not already connected
        if not hasattr(db, 'session'):
            connect_db(self.app)

        # Bind the existing SQLAlchemy instance to the app
        self.db = db
        self.db.init_app(self.app)

        # Create a test database and bind it to the app
        with self.app.app_context():
            self.db.create_all()

        # Create a test client
        self.client = self.app.test_client()

    def tearDown(self):
        # Remove the test database
        with self.app.app_context():
            self.db.drop_all()

    def test_user_registration(self):
        with self.app.app_context():
            with self.app.test_request_context():
                user = User(
                    first_name='John',
                    last_name='Doe',
                    username='johndoe',
                    email='johndoe@example.com',
                    password='password'
                )
                self.db.session.add(user)
                self.db.session.commit()

                # Check if the user is properly stored in the database
                registered_user = User.query.filter_by(username='johndoe').first()
                self.assertEqual(registered_user.first_name, 'John')
                self.assertEqual(registered_user.last_name, 'Doe')

    def test_user_authentication(self):
        with self.app.app_context():
            with self.app.test_request_context():
                # Create a test user
                user = User(
                    first_name='John',
                    last_name='Doe',
                    username='johndoe',
                    email='johndoe@example.com',
                    password='password'
                )
                self.db.session.add(user)
                self.db.session.commit()

                # Test valid authentication
                response = self.client.post('/login', data={
                    'username': 'johndoe',
                    'password': 'password'
                }, follow_redirects=True)
                self.assertIn(b'Welcome back johndoe', response.data)

                # Test invalid authentication
                response = self.client.post('/login', data={
                    'username': 'johndoe',
                    'password': 'wrong_password'
                }, follow_redirects=True)
                self.assertIn(b'Wrong username or password', response.data)
