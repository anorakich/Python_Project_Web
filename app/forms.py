from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from app.models import User
from wtforms.validators import ValidationError


class LoginForm(FlaskForm):
    username = StringField("username")
    password = PasswordField("password")
    submit = SubmitField("sign in")


class RegisterForm(FlaskForm):
    username = StringField("username")
    password = PasswordField("password")
    submit = SubmitField("register")

class PostForm(FlaskForm):
    text = StringField("text")
    submit = SubmitField("post")
