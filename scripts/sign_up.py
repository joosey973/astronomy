from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import DataRequired
from wtforms import SelectField


class SignUp(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField("Gender", choices=["Male", "Female"], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Submit')