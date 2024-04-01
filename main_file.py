from flask import Flask, render_template, redirect, url_for, request
from scripts.sign_in import SignIn
from scripts.sign_up import SignUp
from scripts.new_password import NewPassword
from data.users import User
from data.data_base_session import data_base_init, new_session
from scripts.password_reset import PasswordReset
from scripts.send_message_to_email import send_email_with_reset, generate_code, send_email_with_switch_confirm
from data.events import Events
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from scripts.check_password import check_password
from events_parser import get_data_from_web_site

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign_in"
app.config['SECRET_KEY'] = 'secret_key'
EMAIL = None
NEW_EMAIL = None
CODE = None
ISSENDED = False
data_base_init("dbs/astronomy_site_users.db")


@login_manager.user_loader
def load_user(user_id):
    data_base_session = new_session()
    return data_base_session.query(User).get(user_id)


@app.route("/astronomy-site/sign_in", methods=['GET', 'POST'])
def sign_in():
    form = SignIn()
    if form.validate_on_submit:
        data_base_session = new_session()
        user = data_base_session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("astronomy_site"))
        if user and not user.check_password(form.password.data):
            return render_template("sign_in.html", message="Incorrect password.", form=form)
    return render_template("sign_in.html", title="Sign in", form=form)


@app.route("/astronomy-site/logout")
@login_required
def logout():  # Функция выхода из профиля.
    logout_user()
    return redirect(url_for("astronomy_site"))


@app.route("/astronomy-site/sign_up", methods=['GET', 'POST'])
def sign_up():  # Функция регистрации пользователя.
    form = SignUp()
    if form.validate_on_submit():
        if request.form['password'] != form.repeat_password.data:
            return render_template('sign_up.html', form=form, message="Passwords don't match.", title='Sign up')
        if check_password(form.repeat_password.data):
            return render_template('sign_up.html', form=form, message="Weak password.", title='Sign up')
        if form.age.data < 14:
            return render_template("sign_up.html", message='You are too young.', form=form, title='Sign up')
        data_base_session = new_session()
        if data_base_session.query(User).filter(User.username == form.username.data).first():
            return render_template("sign_up.html", form=form, message='This user have already registrared.',
                                   title='Sign up')
        if data_base_session.query(User).filter(User.email == form.email.data).first():
            return render_template("sign_up.html", form=form, message="This email is already used.", title="Sign up")
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.age = form.age.data
        user.set_password(request.form['password'])
        user.gender = form.gender.data
        if user.gender == "Female":
            user.profile_image = "/static/images/woman.svg"
        else:
            user.profile_image = "/static/images/man.svg"
        data_base_session.add(user)
        data_base_session.commit()
        return redirect(url_for("astronomy_site"))
    return render_template('sign_up.html', form=form, title='Sign up')


@app.route("/")
def main_function():
    return redirect(url_for("astronomy_site"))


@app.route("/astronomy-site")
def astronomy_site():  # Основная страница сайта.
    return render_template("main_page.html", title="Astronomy-site")


@app.route("/astronomy-site/established_solar_hypotheses")
@login_required
def solar_hypotheses():  # Функция с созданием страницы, с устаявшимися гипотезами формирования Солнечной системы
    return render_template("established_solar_hypotheses.html")


@app.route("/astronomy-site/your_hypotheses")
@login_required
def your_hypotheses():
    return render_template("your_hypotheses.html", title="Your hypotheses")


@app.route("/astronomy-site/astronomical-calendar", methods=['GET', 'POST'])
@login_required
def astro_calendar():  # Функция с созданием страницы астрономического календаря.
    session = new_session()
    events_dict = {}
    if not session.query(Events).all():
        get_data_from_web_site()
    for info in session.query(Events).all():
        events_dict[info.date_of_event] = info.events.split(", ")
    return render_template("astronomical_calendar.html", title="Astronomical calendar", events_dict=events_dict)


@app.route("/astronomy-site/password_reset", methods=['GET', 'POST'])
def password_reset():
    global ISSENDED, EMAIL
    form = PasswordReset()
    if form.validate_on_submit():
        session = new_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user:
            send_email_with_reset(user.email)
            ISSENDED = True
            EMAIL = user.email
            return redirect(url_for("revieve_message_page"))
        return render_template("forgot.html", form=form, title="Reset password", message="There is no such mail.")
    return render_template("forgot.html", form=form, title="Reset password")


@app.route("/astronomy-site/reset_password/revieve_message")
def revieve_message_page():
    if ISSENDED:
        return render_template("message.html", title="Recieve Message")
    return redirect(url_for("password_reset"))


@app.route("/astronomy-site/profile", methods=['POST', 'GET'])
@login_required
def profile():
    global NEW_EMAIL, CODE
    if request.method == 'POST':
        data_base_session = new_session()
        if int(request.form['age']) < 14:
            return render_template("profile.html", message='You are too young.', title='Profile')
        if (request.form['email'] != current_user.email and
                data_base_session.query(User).filter(User.email == request.form['email']).first()):
            return render_template("profile.html", title="Profile",
                                   message="This email is already taken.", user=current_user)
        user = data_base_session.query(User).filter(User.username == current_user.username).first()
        user.age = request.form['age']
        user.gender = request.form['gender']
        if user.gender == 'Female':
            user.profile_image = '/static/images/woman.svg'
        else:
            user.profile_image = "/static/images/man.svg"
        data_base_session.commit()
        data_base_session.close()
        if current_user.email != request.form['email']:
            CODE = generate_code()
            NEW_EMAIL = request.form['email']
            send_email_with_switch_confirm(NEW_EMAIL, CODE)
            return redirect(url_for("confirm_email_with_code"))
        return redirect(url_for("profile"))
    return render_template("profile.html", title="Profile", user=current_user)


@app.route("/astronomy-site/profile/confirm_email_change", methods=['POST', 'GET'])
@login_required
def confirm_email_with_code():
    global NEW_EMAIL, CODE
    if request.method == 'POST':
        if request.form['code'] == '':
            CODE = generate_code()
            print(NEW_EMAIL, CODE)
            send_email_with_switch_confirm(NEW_EMAIL, CODE)
            return render_template("profile_with_code.html", title='Profile')
        elif request.form['code'] != CODE:
            return render_template("profile_with_code.html", title='Profile', message='Incorrect code')
        else:
            data_base_session = new_session()
            user = data_base_session.query(User).filter(User.username == current_user.username).first()
            user.email = NEW_EMAIL
            data_base_session.commit()
            data_base_session.close()
            NEW_EMAIL = None
            CODE = None
            return redirect(url_for("profile"))
    return render_template("profile_with_code.html", title='Profile')


@app.route("/astronomy-site/reset_password/revieve_message/new_password", methods=['GET', 'POST'])
def set_new_password():
    global ISSENDED, EMAIL
    if not ISSENDED:
        return redirect(url_for("password_reset"))
    form = NewPassword()
    if form.validate_on_submit():
        if request.form['password'] == form.password_repeat.data:
            if check_password(form.password_repeat.data):
                return render_template("new_password.html", form=form, message="Weak password.", title='New password')
            data_base_session = new_session()
            user = data_base_session.query(User).filter(User.email == EMAIL).first()
            if user.check_password(form.password.data):
                return render_template("new_password.html", form=form, message="This password is already taken.",
                                       title="New password")
            user.set_password(form.password.data)
            data_base_session.commit()
            data_base_session.close()
            ISSENDED = False
            EMAIL = None
            return redirect(url_for("sign_in"))
        return render_template("new_password.html", form=form, message="Passwords don't match.", title="New password")
    return render_template("new_password.html", form=form, title="New password")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
