from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import DataRequired


class SignUp(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Submit')
