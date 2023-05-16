from flask import Flask, render_template, redirect, flash, jsonify, session, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import LoginForm, SignupForm, EditUserForm, IngredientForm
from models import User, db, connect_db, User, Ingredients, Pantry, Recipe
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

####################
# User endpoints

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
    """User Profile"""

    try:
        user = User.query.get_or_404(user_id)
    except:
        return redirect('/')

    if user != g.user:
            flash('You are not authorized to edit this profile!')
            return redirect('/')
    
    return render_template('user/user_profile.html')


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_profile(user_id):

    try:
        user = User.query.get_or_404(user_id)
    except:
        return redirect('/')
    
    if user != g.user:
        flash('You are not authorized to edit this profile!')
        return redirect('/')

    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate_user(user.username, form.password.data):
            try:
                user.first_name = form.first_name.data
                user.last_name = form.last_name.data
                user.username = form.username.data
                user.email = form.email.data
                db.session.commit()
                flash('Profile updated successfully!')
                return redirect(f'/users/{user.id}')

            except Exception as e:
                return str(e)

        else:
            db.session.rollback()
            flash("Wrong username or password")
            return redirect(f'/users/{g.user.id}')

    else:
        return render_template('user/edit_user.html', form=form)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete User"""

    user = User.query.get_or_404(user_id)
    try:
        do_logout()
        db.session.delete(user)
        db.session.commit()
        flash('Account deleted successfully')
        return redirect('/')

    except Exception as e:
        return str(e)

###################################### 
 # Misc Pages

@app.route('/')
def home_page():
    """Render Home Page"""
    
    return render_template('home.html')

######################################
# Ingredients' Endpoints

@app.route('/users/<int:user_id>/ingredients')
def show_ingredients(user_id):
    """Show List of ingredients the User Added"""

    ingredients = Ingredients.query.filter_by(user_id=g.user.id).all()

    return render_template('/ingredients/ingredients.html', ingredients=ingredients)

@app.route('/ingredients/<int:ingredient_id>')
def ingredient_details(ingredient_id):
    """Show an Ingredient's Details"""

    ingredient = Ingredients.query.get_or_404(ingredient_id)

    return render_template('/ingredients/ingredient_details.html', ingredient=ingredient)

@app.route('/ingredients/<int:ingredient_id>/edit', methods=['GET', 'POST'])
def edit_ingredient(ingredient_id):
    """Edit Ingredient"""

    if not g.user:
        return redirect('/')

    ingredient = Ingredients.query.get(ingredient_id)

    if not ingredient:
        flash("The requested ingredient doesn't exist")
        return redirect(f'/users/{g.user.id}/ingredients')

    form = IngredientForm(obj=ingredient)

    if form.validate_on_submit():
        ingredient.name = form.name.data
        ingredient.category = form.category.data

        try:
            db.session.commit()
            flash('Ingredient updated successfully!')
            return redirect(f'/users/{g.user.id}/ingredients')
        except:
            db.session.rollback()
            flash('Something was wrong')
    
    else:
        return render_template('ingredients/edit_ingredient.html', form=form, ingredient=ingredient)

@app.route('/ingredients/add', methods=['GET', 'POST'])
def add_ingredient():

    if not g.user:
        return redirect('/')

    form = IngredientForm()
    if form.validate_on_submit():
        try:
            new_ingredient = Ingredients(name=form.name.data, category=form.category.data)
            g.user.ingredient.append(new_ingredient)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'An issue occured: {str(e)}')
    
    else:
        return render_template('ingredients/add_ingredient.html', form=form)

@app.route('/ingredients/<int:ingredient_id>/delete')
def delete_ingredient(ingredient_id):

    ingredient = Ingredients.query.get(ingredient_id)

    if not ingredient:
        return redirect(f'/users/{g.user.id}/ingredients')
    
    try:
        db.session.delete(ingredient)
        db.session.commit()
        flash(f'{ingredient.name} deleted')
    
    except:
        db.session.rollback()
        flash(f"Couldn't delete {ingredient.name}")
        return redirect(f'/users/{g.user.id}/ingredients')

################################################