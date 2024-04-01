import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import sender_email, sender_password
import random
from string import ascii_letters as letters


def send_email_with_reset(user_email, url='http://192.168.0.104:5000/'):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = 'Astronomy'
    second_path = 'astronomy-site/reset_password/revieve_message/new_password'
    body = f"Перейдите по ссылке, чтобы сменить пароль: <a href={url + second_path}>Нажми здесь</a>"
    msg.attach(MIMEText(body, 'html'))
    email = smtplib.SMTP('smtp.gmail.com', 587)
    email.starttls()
    email.login(sender_email, sender_password)
    email.send_message(msg)
    email.quit()


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
