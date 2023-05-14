from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    """Users Table"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)


    @classmethod
    def register(cls, first_name, last_name, username, email, password):
        """Registers Users w/ Hashed Password and Returns User"""

        hashed_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(first_name = first_name, last_name = last_name, username = username, email = email, password = hashed_password)
        
        db.session.add(user)
        return user

    @classmethod
    def authenticate_user(cls, username, password):
        """Authenticates Users and Returns User"""
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Ingredients(db.Model):
    """Ingredients Table"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, expiry_date):
        self.name = name
        self.expiry_date = expiry_date

    def is_expired(self):
        """Helper function to keep the user aware of expired items in order to remove from pantry and frontend"""
        return self.expiry_date < datetime.now()

    def check_expired_items():
        """Add APScheduler and Socketio to Schedule Daily Check on Inventory Expiry Eates and Notify User"""
        """Maybe better to place inside pantry"""
        pass

def connect_db(app):
    db.app = app
    db.init_app(app)
