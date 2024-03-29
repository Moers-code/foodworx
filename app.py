from flask import Flask, render_template, redirect, flash, jsonify, session, g, request
from flask_debugtoolbar import DebugToolbarExtension
from forms import LoginForm, SignupForm, EditUserForm, IngredientForm, PantryForm
from models import User, db, connect_db, User, Ingredients, Pantry, Recipe, APIDATA
from flask_migrate import Migrate
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
import re

load_dotenv()
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USERNAME}:{PASSWORD}@mahmud.db.elephantsql.com/{USERNAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

API_KEY = os.getenv('API_KEY')

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
        

    if form.validate_on_submit():
        try:
            user = User.register(first_name = form.first_name.data, last_name = form.last_name.data,
                            username = form.username.data, email = form.email.data, password = form.password.data)

            db.session.commit()
            do_login(user)
            flash(f'{user.username} created successfully!', category='success')   
            return redirect(f'/users/{user.id}')

        except Exception as e:
            db.session.rollback()
            flash(f"Couldn't create user, {str(e)}", category='error')
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
            flash(f'Welcome back {user.username}', category='success')
            return redirect(f'/users/{user.id}')
        else:
            flash('Wrong username or password. Please try again.', category='error')
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
            flash('You are not authorized to edit this profile!', category='error')
            return redirect('/')

    form=LoginForm()
    pantry_items = Pantry.query.filter_by(user_id=user.id).all()
    return render_template('user/user_profile.html', form=form, pantry_items=pantry_items)


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_profile(user_id):

    try:
        user = User.query.get_or_404(user_id)
    except:
        return redirect('/')
    
    if user != g.user:
        flash('You are not authorized to edit this profile!', category='error')
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
                flash('Profile updated successfully!', category='success')
                return redirect(f'/users/{user.id}')

            except Exception as e:
                return str(e)

        else:
            db.session.rollback()
            flash("Wrong username or password", category='error')
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
        flash('Account deleted successfully', category='success')
        return redirect('/')

    except Exception as e:
        return f'Error {str(e)}'

###################################### 
 # Misc Pages

@app.route('/')
def home_page():
    """Render Home Page"""
    
    return render_template('home.html')

######################################
# Ingredients Endpoints

@app.route('/users/<int:user_id>/ingredients')
def show_ingredients(user_id):
    """Show List of ingredients the User Added"""

    ingredients = Ingredients.query.filter_by(user_id=g.user.id).all()

    return render_template('/ingredients/ingredients.html', ingredients=ingredients)

@app.route('/ingredients/<int:ingredient_id>')
def ingredient_details(ingredient_id):
    """Show an Ingredient's Details"""

    ingredient = Ingredients.query.get_or_404(ingredient_id)
    form = IngredientForm()

    return render_template('/ingredients/ingredient_details.html', ingredient=ingredient, form=form)

@app.route('/ingredients/<int:ingredient_id>/edit', methods=['GET', 'POST'])
def edit_ingredient(ingredient_id):
    """Edit Ingredient"""

    if not g.user:
        return redirect('/')

    ingredient = Ingredients.query.get(ingredient_id)

    if not ingredient:
        flash("The requested ingredient doesn't exist", category='error')
        return redirect(f'/users/{g.user.id}/ingredients')

    form = IngredientForm(obj=ingredient)

    if form.validate_on_submit():
        ingredient.name = form.name.data
        ingredient.category = form.category.data

        try:
            db.session.commit()
            flash('Ingredient updated successfully!', category='success')
            return redirect(f'/users/{g.user.id}/ingredients')
        except:
            db.session.rollback()
            flash('Something was wrong', category='error')
    
    else:
        return render_template('ingredients/edit_ingredient.html', form=form, ingredient=ingredient)

@app.route('/ingredients/add', methods=['GET', 'POST'])
def add_ingredient():
    """Add Ingredient"""

    if not g.user:
        return redirect('/')

    form = IngredientForm()
    if form.validate_on_submit():
        try:
            new_ingredient = Ingredients(name=form.name.data, category=form.category.data)
            g.user.ingredient.append(new_ingredient)
            db.session.commit()
            return redirect(f'/users/{g.user.id}/ingredients')

        except Exception as e:
            db.session.rollback()
            flash(f'An issue occured: {str(e)}')
    
    else:
        return render_template('ingredients/add_ingredient.html', form=form)

@app.route('/ingredients/<int:ingredient_id>/delete', methods=['POST'])
def delete_ingredient(ingredient_id):
    """Delete Ingredient"""

    ingredient = Ingredients.query.get(ingredient_id)

    if not ingredient:
        return redirect(f'/users/{g.user.id}/ingredients')
    
    try:
        db.session.delete(ingredient)
        db.session.commit()
        flash(f'{ingredient.name} deleted', category='success')
        
    except:
        db.session.rollback()
        flash(f"Couldn't delete {ingredient.name}", category='error')
        
    return redirect(f'/users/{g.user.id}/ingredients')
################################################
# Pantry Endpoints

@app.route('/users/<int:user_id>/pantryitems')
def show_pantry(user_id):
    """Show List of User's Pantry Items"""

    user = User.query.get(user_id)
    if user.id != g.user.id:
        flash('You are not authorized to view this page', category='error')
        return redirect('/')

    pantry = Pantry.query.filter_by(user_id=user_id).all()
    
    return render_template('pantry/pantry_items.html', pantry=pantry)

@app.route('/pantryitems/<int:item_id>')
def item_details(item_id):
    """Show Ingredient Details"""

    item = Pantry.query.get_or_404(item_id)
    if not item:
        return redirect('users/{g.user.id}/pantryitems')

    return render_template('pantry/item_details.html', item=item)

@app.route('/pantryitems/add', methods=['GET', 'POST'])
def add_item():
    """Add New Item to the Pantry"""

    
    if not g.user:
        return redirect('/')
    
    form = PantryForm()

    # if we want to give user the ability to add ingredients from what he added to ingredients
    # form.ingredient.choices = [(int(i.id), i.name) for i in Ingredients.query.filter_by(user_id=g.user.id).all()]

    if form.validate_on_submit():
        
        try:
            ingredient_name = form.ingredient_name.data
            ingredient_quantity=form.ingredient_quantity.data
            uom=form.uom.data
            expiry_date = form.expiry_date.data
            pantry_item = Pantry(user_id=g.user.id, ingredient_name=ingredient_name, ingredient_quantity=ingredient_quantity, expiry_date=expiry_date, uom=uom)
            g.user.pantry.append(pantry_item)
            db.session.commit()
            flash('Pantry item added successfully.', category='success')
            return redirect(f'/users/{g.user.id}/pantryitems')

        except Exception as e:
            db.session.rollback()
            flash(f'An issue occurred: line 321 {str(e)}', category='error')

    return render_template('pantry/add_item.html', form=form)

@app.route('/pantryitems/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    """Edit Pantry Item"""

    if not g.user:
        return redirect('/')

    item = Pantry.query.get(item_id)
    
    if not item:
        flash("The requested item doesn't exist", category='error')
        return redirect(f'/users/{g.user.id}/pantryitems')

    form = PantryForm(obj=item)

    if form.validate_on_submit():
        item.ingredient_name=form.ingredient_name.data
        item.ingredient_quantity=form.ingredient_quantity.data
        item.uom=form.uom.data
        item.expiry_date = form.expiry_date.data

        try:   
            db.session.commit()
            flash('Pantry item edited successfully.', category='success')
            return redirect(f'/users/{g.user.id}/pantryitems')
    
        except:
            db.session.rollback()
            flash('Something was wrong', category='error')
    
    else:
        return render_template('pantry/edit_item.html', form=form, item=item)


@app.route('/pantryitems/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    """Delete Pantry Item"""

    item = Pantry.query.get(item_id)

    if not item:
        return redirect(f'/users/{g.user.id}/pantryitems')
    else:
        try:
            db.session.delete(item)
            db.session.commit()
            flash(f'{item.ingredient_name} deleted', category='success')

        except Exception as e:
            db.session.rollback()
            flash(f"Couldn't delete {item.ingredient_name}: {str(e)}", category='error')
        return redirect(f'/users/{g.user.id}/pantryitems')

#####################################################
# Axios requests' endpoints

@app.route('/search')
def get_suggestions():
    """A View that Handles the Search Bar Input and Sends Back Suggestions"""

    user_input = request.args.get('userInput')
    response = []
    ingredients = APIDATA.query.all()
    for ingredient in ingredients:
        if user_input in ingredient.name:
            response.append({'id':ingredient.id, 'name':ingredient.name})

    return jsonify({'response':response})

@app.route('/fetch-recipes', methods=['POST'])
def fetch_recipes():
    """API Request to Fetch Recipes"""

    ingredient_name = request.json.get('ingredientName')
    ingredient_name = re.sub(r'\s', '_', ingredient_name)

    res = requests.get(f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredient_name}&number=6&apiKey={API_KEY}')
    recipes = res.json()
  
    response_data = []

    for recipe in recipes:
        recipe_data = {
            'title': recipe['title'],
            'image': recipe['image'],
        'ingredients': []
        }

        for ingredient in recipe['usedIngredients']:
            recipe_data['ingredients'].append(ingredient['original'])
        
        for ingredient in recipe['missedIngredients']:
            recipe_data['ingredients'].append(ingredient['original'])
        response_data.append(recipe_data)

    return jsonify(response_data)

