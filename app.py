from flask import Flask, render_template, redirect, flash, jsonify, session
from flask_debugtoolbar import DebugToolbarExtension
from forms import LoginForm, SignupForm
from models import User, db, connect_db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///foodworx'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "H-pful™•¶,it+wo98" 

debug = DebugToolbarExtension(app)


with app.app_context():
    connect_db(app)
    db.create_all()

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register_user():
    """Register New Users"""

    form = SignupForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash(f'{username} already exists. Choose another username.')
            return redirect('/register')
        else:
            user = User.register(first_name = first_name, last_name = last_name,
                             username = username, email = email, password = password)
    
            try:
                db.session.add(user)
                db.session.commit()
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
        user = User.autheticate_user(username=username, password=password)

        if user:
            session['user_id'] = user.id
            flash(f'Welcome back {user.username}')
            return redirect(f'/users/{user.id}')
        else:
            flash('Wrong username or password. Please try again.')
            return redirect('/login')
    else:
        return render_template('user/login.html', form=form)