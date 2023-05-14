from flask import Flask, render_template, redirect, flash, jsonify, session, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import LoginForm, SignupForm
from models import User, db, connect_db
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///foodworx'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "H-pful™•¶,it+wo98" 

debug = DebugToolbarExtension(app)
migrate = Migrate(app, db)

CURR_USER_KEY = 'user_id'

with app.app_context():
    connect_db(app)
    db.create_all()


@app.before_request
def add_user_to_g():
    """Add Logged-In User to Flask Global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log User In """
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Log User Out"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register_user():
    """Register New Users"""

    form = SignupForm()

    user = User.query.filter_by(username=form.username.data).first()

    if user:
        flash(f'{user.username} already exists. Choose another username.')
        return redirect('/login')

    if form.validate_on_submit():
        try:
            user = User.register(first_name = form.first_name.data, last_name = form.last_name.data,
                            username = form.username.data, email = form.email.data, password = form.password.data)

            db.session.commit()
            do_login(user)
            flash(f'{user.username} created successfully!')   
            return redirect(f'/users/{user.id}')

        except Exception as e:
            db.session.rollback()
            flash(f"Couldn't create user, {str(e)}", 'error')
            return redirect('/register')

        
    else:
        return render_template('user/signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_users():
    """Login Users"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate_user(username=username, password=password)

        if user:
            do_login(user)
            flash(f'Welcome back {user.username}')
            return redirect(f'/users/{user.id}')
        else:
            flash('Wrong username or password. Please try again.')
            return redirect('/login')
    else:
        return render_template('user/login.html', form=form)

@app.route('/logout')
def logout():
    """Log User Out"""

    do_logout()
    return redirect('/login')


@app.route('/users/<int:user_id>')
def user_profile(user_id):

    if g.user.id == user_id:
        
        return render_template('user/user_profile.html')
