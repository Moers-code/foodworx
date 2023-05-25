from unittest import TestCase
from models import User, Pantry, db, bcrypt, connect_db
import os

os.environ['DATABASE_URL'] = 'postgresql:///test_foodworx'

from app import app
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_ECHO'] = False

test_app = app.test_client()

class TestPantry(TestCase):
    """Tests for Pantry Model"""

    def setUp(self):
        with app.app_context():
            db.create_all()
            self.user = User.register(first_name='new', last_name='test', username='test user', email='test@test.com', password='password')
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_item(self):
        with app.app_context():
            item = Pantry(user_id=self.user.id, ingredient_name='apple', ingredient_quantity=1.0, expiry_date='2023-05-28', uom='kg')
            self.user.pantry.append(item)
            db.session.add(item)
            db.session.commit()
            
            self.assertIsNotNone(item)
            self.assertEqual(item.ingredient_name, 'apple')
            self.assertEqual(item.user_id, 1)
            