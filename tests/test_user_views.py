from unittest import TestCase
from app import app
from models import db, User, connect_db

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_foodworx'
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_ECHO'] = False
app.config['WTF_CSRF_ENABLED'] = False

class TestUserViews(TestCase):
    """Tests for User Views"""

    def setUp(self):
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            
    
    def test_registration(self):
        with app.test_client() as client:
            res = client.post('/register',data={'first_name':'new', 'last_name':'test', 'username':'test user', 'email':'test@test.com', 'password':'password'})

            self.assertEqual(res.status_code, 200)
            # self.assertTrue(res.location, f'/users/{self.user.id}')
            