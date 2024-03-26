from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField
from wtforms.validators import DataRequired


class PasswordReset(FlaskForm):
    email = EmailField("Enter email", validators=[DataRequired()])
    submit = SubmitField("Submit")
