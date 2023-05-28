from unittest import TestCase
from datetime import date
from flask import Flask
from models import User, Pantry, connect_db, db

class PantryModelTestCase(TestCase):
    def setUp(self):
        # Create a test Flask app
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///foodworx-test'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

    def test_days_left(self):
        # Test the days_left property
        with self.app.app_context():
            # Create a test user
            user = User.register(
                first_name='John',
                last_name='Doe',
                username='johndoe',
                email='johndoe@example.com',
                password='password'
            )
            self.db.session.commit()

            # Create a test pantry item
            pantry_item = Pantry(
                user_id=user.id,
                ingredient_name='Tomato',
                ingredient_quantity=2.5,
                expiry_date=date.today(),
                uom='kg'
            )
            self.db.session.add(pantry_item)
            self.db.session.commit()

            # Test the days_left property
            self.assertEqual(pantry_item.days_left, 0)
            
