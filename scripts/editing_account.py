from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired


class EditingAccount(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    gender = SelectField("Gender", choices=["Male", "Female"], validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")