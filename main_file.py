from flask import Flask, render_template, redirect, url_for, request, session
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
# login_manager.login_view = "sign_in"
app.config['SECRET_KEY'] = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
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
def astronomy_sign_up():  # Функция регистрации пользователя.
    form = SignUp()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
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
        user.set_password(form.password.data)
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
@app.route("/astronomy-site")
def astronomy_site():  # Основная страница сайта.
    return render_template("main_page.html", title="Astronomy-site")


@app.route("/astronomy-site/profile")
@login_required
def profile():
    form = EditingAccount()
    if form.validate_on_submit():
        pass
    return render_template("profile.html", title="Profile", form=form)


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


# @app.route("/astronomy-site/new_password", methods=["GET", "POST"])
# def new_password():  # Функция установки нового пароля.
#     global ISSENDED, MAIN_USER
#     if not ISSENDED:
#         return redirect(url_for("astronomy_site"))
#     form = NewPassword()
#     if form.validate_on_submit():
#         if form.password.data == form.password_repeat.data:
#             global_init("db/astronomy_site_users.db")
#             session = create_session()
#             user = session.query(User).filter(User.email == EMAIL).first()
#             setattr(user, "password", user.set_password(form.password.data))
#             session.commit()
#             MAIN_USER = user
#             ISSENDED = False
#             return redirect(url_for("astronomy_site"))
#         return render_template("new_password.html", form=form, message="Passwords don't match", title="New password")
#     return render_template("new_password.html", form=form, title="New password")


# @app.route("/astronomy-site/password_reset", methods=["GET", "POST"])
# def password_reset():  # Функция сброса пароля
#     global EMAIL, ISSENDED
#     form = PasswordReset()
#     if form.validate_on_submit():
#         global_init("db/astronomy_site_users.db")
#         session = create_session()
#         user = session.query(User).filter(User.email == form.email.data).first()
#         if user:
#             send_email(user.email)
#             ISSENDED = True
#             EMAIL = form.email.data
#             return render_template("message.html", title="Message")
#         return render_template("forgot.html", form=form, title="Reset password", message="There is no such mail")
#     return render_template("forgot.html", form=form, title="Reset password")


# @app.route("/astronomy-site/profile")
# def profile():  # Функция изменения профиля.
#     form = EditingAccount()
#     form.username.data = MAIN_USER.username
#     form.age.data = MAIN_USER.age
#     form.gender.data = MAIN_USER.gender
#     form.password.data = MAIN_USER.hashed_password
#     return render_template("profile.html", title="Profile", user=MAIN_USER, form=form)


# @app.route("/astronomy-site/astronomy_sign_in", methods=['GET', 'POST'])
# def astronomy_sign_in():  # Функция захода в чуществующий аккаунт.
#     global MAIN_USER
#     form = SignIn()
#     if form.validate_on_submit():
#         global_init("db/astronomy_site_users.db")
#         session = create_session()
#         user = session.query(User).filter(
#             User.username == form.username.data).first()
#         if user and user.check_password(form.password.data):
#             MAIN_USER = user
#             return redirect(url_for('astronomy_site'))
#         else:
#             return render_template("sign_in.html", form=form, message='Incorrect password.', title='Sign in')
#     return render_template('sign_in.html', form=form, title='Sign in')
if __name__ == "__main__":
    app.run(host="0.0.0.0")
