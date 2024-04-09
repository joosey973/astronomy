from flask_wtf import FlaskForm
from wtforms import (BooleanField, EmailField, IntegerField, PasswordField,
                     SelectField, StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import sender_email, sender_password
import random
from string import ascii_letters as letters


def check_password(password):
    return (len(password) < 8 or len([letter for letter in password if letter.isupper()]) == 0 or
            len([letter for letter in password if letter.islower()]) == 0 or
            len([letter for letter in password if letter in '_@$!%*?&.']) == 0)


class NewPassword(FlaskForm):
    repeat_password = PasswordField("Repeat password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RecordForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


def generate_code():
    code_generator = ([str(random.randrange(0, 10)) for i in range(3)] +
                      [random.choice(" ".join(letters).split()) for i in range(3)]
                      )
    return "".join(code_generator)


def send_email_with_switch_confirm(user_email, code):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = 'Astronomy'
    body = f"Your code is {code}"
    msg.attach(MIMEText(body, 'html'))
    email = smtplib.SMTP('smtp.gmail.com', 587)
    email.starttls()
    email.login(sender_email, sender_password)
    email.send_message(msg)
    email.quit()


class SignIn(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField('Submit')


class SignUp(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField("Gender", choices=["Male", "Female"], validators=[DataRequired()])
    repeat_password = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = TextAreaField("Your comment", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CommentUpdateForm(FlaskForm):
    body = TextAreaField("Your comment", validators=[DataRequired()])
    submit = SubmitField("Submit")
