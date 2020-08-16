from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp


class Load_Script(FlaskForm):
    github_url = StringField('Github URL', [
        DataRequired()
    ])
    submit = SubmitField('Sign In')
