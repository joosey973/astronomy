from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired


class NewPassword(FlaskForm):
    password = PasswordField("Enter password", validators=[DataRequired()])
    password_repeat = PasswordField("Repeat password", validators=[DataRequired()])
    submit = SubmitField("Submit")
