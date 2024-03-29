from flask_sqlalchemy import SQLAlchemy
from datetime import date
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
    recipe = db.relationship('Recipe', backref='user', cascade="all, delete-orphan")
    pantry = db.relationship('Pantry', backref='user', cascade="all, delete-orphan")
    ingredient = db.relationship('Ingredients', backref='user', cascade="all, delete-orphan")
    
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

    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    
    

class Recipe(db.Model):
    """Favorite Recipes Table"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

class Pantry(db.Model):
    """Pantry Table"""

    __tablename__ = 'pantry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    ingredient_name = db.Column(db.Text)
    ingredient_quantity = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    uom = db.Column(db.Text, nullable=False)

    @property
    def days_left(self):
        today = date.today()
        return (self.expiry_date - today).days
        
    # def is_expired(self):
    #     """Helper function to keep the user aware of expired items in order to remove from pantry and frontend"""
    #     return self.expiry_date < datetime.now()

    # def check_expired_items():
    #     """Add APScheduler and Socketio to Schedule Daily Check on Inventory Expiry Eates and Notify User"""
    #     """Maybe better to place inside pantry"""
    #     pass

class APIDATA(db.Model):
    """Ingredients Names and ID Downloaded From the API"""

    __tablename__ = 'apidata'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

def connect_db(app, db_uri=None):
    """Connect the database to the Flask app."""
    if db_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)