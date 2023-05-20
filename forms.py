from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SelectField, DateField
from wtforms.validators import Email, DataRequired, EqualTo, Length
from models import Ingredients
from flask import g

class SignupForm(FlaskForm):
    """Form for Registering Users"""
    
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(min=1, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords Must Match')])


class LoginForm(FlaskForm):
    """Form for Logging in Users"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class EditUserForm(FlaskForm):
    """Form to Edit User Info"""

    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(min=1, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    

class ChangePasswordForm(FlaskForm):
    pass


class IngredientForm(FlaskForm):
    """Form to Add/Edit a New Ingredient"""

    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=50)])
    category = StringField('Category')

class PantryForm(FlaskForm):
    """Form to Add/Edit a New Pantry Item"""

    ingredient = StringField('Ingredient', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', validators=[DataRequired()])
    uom = SelectField('Unit', choices=[('mg', 'mg'), ('g', 'g'), ('kg', 'kg'), ('ml', 'ml'), ('L', 'L'), ('pc', 'pc')], validators=[DataRequired()])

