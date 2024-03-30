from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired


class NewPassword(FlaskForm):
    repeat_password = PasswordField("Repeat password", validators=[DataRequired()])
    submit = SubmitField("Submit")
