import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import sender_email, sender_password


def send_email(user_email):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = 'Astronomy'
    body = 'Перейдите по ссылке, чтобы сменить пароль: <a href="http://127.0.0.1:8080/astronomy-site/new_password">Нажми здесь</a>'
    msg.attach(MIMEText(body, 'html'))
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.starttls()
    smtpObj.login(sender_email, sender_password)
    smtpObj.send_message(msg)
    smtpObj.quit()