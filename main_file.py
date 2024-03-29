from flask import Flask, render_template, redirect, url_for, request
import datetime
from scripts.sign_in import SignIn
from scripts.sign_up import SignUp
from scripts.new_password import NewPassword
from data.users import User
from data.db_session import global_init, create_session
from scripts.password_reset import PasswordReset
from scripts.send_message_to_email import send_email
from scripts.editing_account import EditingAccount
from data.events import Events
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign_in"
app.config['SECRET_KEY'] = 'secret_key'
EMAIL = None
ISSENDED = False


@login_manager.user_loader
def load_user(user_id):
    global_init("db/astronomy_site_users.db")
    db_session = create_session()
    return db_session.query(User).get(user_id)


@app.route("/astronomy-site/sign_in", methods=['GET', 'POST'])
def sign_in():
    form = SignIn()
    if form.validate_on_submit:
        global_init("db/astronomy_site_users.db")
        db_session = create_session()
        user = db_session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            print(f"Запомнить меня: {form.remember_me.data}")
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("astronomy_site"))
        if user and not user.check_password(form.password.data):
            return render_template("sign_in.html", message="Incorrect username or password.", form=form)
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
        global_init("db/astronomy_site_users.db")
        db_session = create_session()
        if db_session.query(User).filter(User.username == form.username.data).first():
            return render_template("sign_up.html", form=form, message='This user have already registrared.',
                                   title='Sign up')
        if db_session.query(User).filter(User.email == form.email.data).first():
            return render_template("sign_up.html", form=form, message="This email is already used", title="Sign up")
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
        db_session.add(user)
        db_session.commit()
        return redirect(url_for("astronomy_site"))
    return render_template('sign_up.html', form=form, title='Sign up')


@app.route("/")
def main_function():
    return redirect(url_for("astronomy_site"))


@app.route("/astronomy-site")
def astronomy_site():  # Основная страница сайта.
    return render_template("main_page.html", title="Astronomy-site")


@app.route("/astronomy-site/stable_solar_hypotheses")
@login_required
def solar_hypotheses():  # Функция с созданием страницы, с устаявшимися гипотезами формирования Солнечной системы
    return render_template("stable_solar_hypotheses.html")


@app.route("/astronomy-site/your_hypotheses")
@login_required
def your_hypotheses():
    return render_template("your_hypotheses.html", title="Your hypotheses")


@app.route("/astronomy-site/astronomical-calendar", methods=['GET', 'POST'])
@login_required
def astro_calendar():  # Функция с созданием страницы астрономического календаря.
    global_init("db/astronomy_site_users.db")
    session = create_session()
    events_dict = {}
    for info in session.query(Events).all():
        events_dict[info.date_of_event] = info.events.split(", ")
    return render_template("astronomy_calendar.html", title="Astronomical calendar", events_dict=events_dict)


@app.route("/astronomy-site/password_reset", methods=['GET', 'POST'])
def password_reset():
    global ISSENDED, EMAIL
    form = PasswordReset()
    if form.validate_on_submit():
        global_init("db/astronomy_site_users.db")
        session = create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user:
            send_email(user.email)
            ISSENDED = True
            EMAIL = user.email
            return redirect(url_for("revieve_message_page"))
        return render_template("forgot.html", form=form, title="Reset password", message="There is no such mail")
    return render_template("forgot.html", form=form, title="Reset password")


@app.route("/astronomy-site/reset_password/revieve_message")
def revieve_message_page():
    if ISSENDED:
        return render_template("message.html", title="Recieve Message")
    return redirect(url_for("password_reset"))


@app.route("/astronomy-site/profile", methods=['POST', 'GET'])
@login_required
def profile():
    print(current_user.age)
    if request.method == 'POST':
        global_init("db/astronomy_site_users.db")
        db_session = create_session()
        if request.form['email'] != current_user.email and db_session.query(User).filter(User.email == request.form['email']).first():
            return render_template("profile.html", title="Profile", message="This email is already taken.", user=current_user)
        user = db_session.query(User).filter(User.username == current_user.username).first()
        user.age = request.form['age']
        print("asas")
        if request.form['gender'] == 'Female':
            user.gender = '/static/images/woman.svg'
        else:
            user.gender = "/static/images/man.svg"
        db_session.commit()
        db_session.close()
        # print(user.gender, request.form['gender'])
        return redirect(url_for("astronomy_site"))
    return render_template("profile.html", title="Profile", user=current_user)


@app.route("/astronomy-site/reset_password/revieve_message/new_password", methods=['GET', 'POST'])
def set_new_password():
    global ISSENDED, EMAIL
    if not ISSENDED:
        return redirect(url_for("password_reset"))
    form = NewPassword()
    if form.validate_on_submit():
        if form.password.data == form.password_repeat.data:
            global_init("db/astronomy_site_users.db")
            db_session = create_session()
            user = db_session.query(User).filter(User.email == EMAIL).first()
            if user.check_password(form.password.data):
                return render_template("new_password.html", form=form, message="This password is already taken",
                                       title="New password")
            user.set_password(form.password.data)
            db_session.commit()
            ISSENDED = False
            EMAIL = None
            return redirect(url_for("sign_in"))
        return render_template("new_password.html", form=form, message="Passwords don't match", title="New password")
    return render_template("new_password.html", form=form, title="New password")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
