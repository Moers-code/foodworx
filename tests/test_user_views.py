from unittest import TestCase
from flask import current_app
from models import User, connect_db, db
from app import app


class UserTestCase(TestCase):
 
    def setUp(self):
        # Use the main application instance
        self.app = app
        self.app_context = app.app_context()
        self.app_context.push()

        # Configure the test database URI
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///foodworx-test'

        # Connect the database to the Flask app if not already connected
        if not hasattr(db, 'session'):
            connect_db(self.app)

        # Assign db to self.db
        self.db = db

        # Create the test database
        with self.app_context:
            self.db.create_all()

        # Create a test client
        self.client = self.app.test_client()

    def tearDown(self):
        # Remove the test database
        with self.app.app_context():
            self.db.drop_all()


# from unittest import TestCase
# from flask import Flask
# from models import User, connect_db, db


# class UserTestCase(TestCase):
    
#     def setUp(self):
#         # Create a test Flask app
#         self.app = Flask(__name__)
#         self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///foodworx-test'  # Test database URI
#         self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#         self.app.config['TESTING'] = True
#         self.app.config['WTF_CSRF_ENABLED'] = False
    
#         # Connect the database to the Flask app if not already connected
#         if not hasattr(db, 'session'):
#             connect_db(self.app)

#         # Bind the existing SQLAlchemy instance to the app
#         self.db = db
#         self.db.init_app(self.app)

#         # Create a test database and bind it to the app
#         with self.app.app_context():
#             self.db.create_all()

#         # Create a test client
#         self.client = self.app.test_client()

#         # Set up the application context
#         self.app_context = self.app.app_context()
#         self.app_context.push()
        
#     def tearDown(self):
#         # Remove the test database
#         with self.app.app_context():
#             self.db.drop_all()

    def test_user_registration(self):
        response = self.client.post('/register', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'password'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # Add additional assertions to verify the user registration process
        self.assertIn(b'User created successfully', response.data)
        # Assert the redirected page or the page content after successful registration
        # For example, you can assert the presence of the user's name on the page
        self.assertIn(b'Welcome, John', response.data)
            # Add additional assertions to test the expected behavior



        # Check if the user is properly stored in the database
        # registered_user = User.query.filter_by(username='johndoe').first()
        # self.assertEqual(registered_user.first_name, 'John')
        # self.assertEqual(registered_user.last_name, 'Doe')

    # def test_user_authentication(self):
    #     # Create a test user
    #     user = User(
    #         first_name='John',
    #         last_name='Doe',
    #         username='johndoe',
    #         email='johndoe@example.com',
    #         password='password'
    #     )
    #     self.db.session.add(user)
    #     self.db.session.commit()

    #     # Test valid authentication
    #     response = self.client.post('/login', data={
    #         'username': 'johndoe',
    #         'password': 'password'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Welcome back johndoe', response.data)

    #     # Test invalid authentication
    #     response = self.client.post('/login', data={
    #         'username': 'johndoe',
    #         'password': 'wrong_password'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Wrong username or password', response.data)
