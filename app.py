from flask import Flask, render_template, redirect, flash, jsonify, session, g, request
from flask_debugtoolbar import DebugToolbarExtension
from forms import LoginForm, SignupForm, EditUserForm, IngredientForm, PantryForm
from models import User, db, connect_db, User, Ingredients, Pantry, Recipe, APIDATA
from flask_migrate import Migrate
from datetime import datetime

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
    form=LoginForm()
    return render_template('user/user_profile.html', form=form)


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
        flash(f'{ingredient.name} deleted')
        
    except:
        db.session.rollback()
        flash(f"Couldn't delete {ingredient.name}")
        
    return redirect(f'/users/{g.user.id}/ingredients')
################################################
# Pantry Endpoints

@app.route('/users/<int:user_id>/pantryitems')
def show_pantry(user_id):
    """Show List of User's Pantry Items"""

    user = User.query.get(user_id)
    if user.id != g.user.id:
        flash('You are not authorized to view this page')
        return redirect('/')

    pantry = Pantry.query.filter_by(user_id=user_id).all()
    
    return render_template('pantry/pantry_items.html', pantry=pantry)

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
            ingredient_name = form.ingredient.data
            quantity=form.quantity.data
            uom=form.uom.data
            expiry_date = form.expiry_date.data
            pantry_item = Pantry(user_id=g.user.id, ingredient_name=ingredient_name, ingredient_quantity=quantity, expiry_date=expiry_date, uom=uom)
            g.user.pantry.append(pantry_item)
            db.session.commit()
            flash('Pantry item added successfully.')
            return redirect(f'/users/{g.user.id}/pantryitems')

        except Exception as e:
            db.session.rollback()
            flash(f'An issue occurred: line 321 {str(e)}')

    return render_template('pantry/add_item.html', form=form)

@app.route('/pantryitems/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    """Edit Pantry Item"""

    if not g.user:
        return redirect('/')

    item = Pantry.query.get(item_id)
    
    if not item:
        flash("The requested item doesn't exist")
        return redirect(f'/users/{g.user.id}/pantryitems')

    form = PantryForm(obj=item)
    print(item.ingredient_name)
    if form.validate_on_submit():
        item.ingredient_name=form.ingredient.data
        item.ingredient_quantity=form.quantity.data
        item.uom=form.uom.data
        item.expiry_date = datetime.strptime(form.expiry_date.data, '%Y-%m-%d')

        try:   
            db.session.commit()
            flash('Pantry item edited successfully.')
            return redirect(f'/users/{g.user.id}/pantryitems')
    
        except:
            db.session.rollback()
            flash('Something was wrong')
    
    else:
        return render_template('pantry/edit_item.html', form=form, item=item)


@app.route('/pantryitems/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    """Delete Pantry Item"""

    item = Pantry.query.get(item_id)

    if not item:
        return redirect(f'/users/{g.user.id}/pantryitems')
    
    try:
        db.session.delete(item)
        db.session.commit()
        flash(f'{item.name} deleted')
    
    except:
        db.session.rollback()
        flash(f"Couldn't delete {item.ingredient_name}")
        return redirect(f'/users/{g.user.id}/ingredients')

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