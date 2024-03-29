from flask import Flask, render_template, redirect, url_for
from scripts.sign_in import SignIn
from scripts.sign_up import SignUp
from scripts.new_password import NewPassword
from data.users import User
from data.db_session import global_init, create_session
from scripts.password_reset import PasswordReset
from scripts.send_message_to_email import send_email
from editing_account import EditingAccount
from data.events import Events

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
MAIN_USER = None
EMAIL = None
ISSENDED = False


@app.route("/astronomy-site")
def astronomy_site():  # Основная страница сайта.
    return render_template("main_page.html", title="astronomy-site", user=MAIN_USER)


@app.route("/astronomy-site/your_hypotheses")
def your_hypotheses():  # Страница с гипотезами пользователей
    if MAIN_USER:
        return render_template("your_hypotheses.html", user=MAIN_USER, title="Your hypotheses")
    return redirect("/astronomy-site/astronomy_sign_in")


@app.route("/astronomy-site/new_password", methods=["GET", "POST"])
def new_password():  # Функция установки нового пароля.
    global ISSENDED, MAIN_USER
    if not ISSENDED:
        return redirect("/astronomy-site")
    form = NewPassword()
    if form.validate_on_submit():
        if form.password.data == form.password_repeat.data:
            global_init("db/astronomy_site_users.db")
            session = create_session()
            user = session.query(User).filter(User.email == EMAIL).first()
            setattr(user, "password", user.set_password(form.password.data))
            session.commit()
            MAIN_USER = user
            ISSENDED = False
            return redirect("/astronomy-site")
        return render_template("new_password.html", form=form, message="Passwords don't match", title="New password")
    return render_template("new_password.html", form=form, title="New password")


@app.route("/astronomy-site/password_reset", methods=["GET", "POST"])
def password_reset():  # Функция сброса пароля
    global EMAIL, ISSENDED
    form = PasswordReset()
    if form.validate_on_submit():
        global_init("db/astronomy_site_users.db")
        session = create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user:
            send_email(user.email)
            ISSENDED = True
            EMAIL = form.email.data
            return render_template("message.html", title="Message")
        return render_template("forgot.html", form=form, title="Reset password", message="There is no such mail")
    return render_template("forgot.html", form=form, title="Reset password")


@app.route("/astronomy-site/stable_solar_hypotheses")
def solar_hypotheses():  # Функция с созданием страницы, с устаявшимися гипотезами формирования Солнечной системы
    if MAIN_USER:
        return render_template("stable_solar_hypotheses.html", user=MAIN_USER)
    return redirect("/astronomy-site/astronomy_sign_in")


@app.route("/astronomy-site/logout")
def logout():  # Функция выхода из профиля.
    global MAIN_USER
    if MAIN_USER:
        MAIN_USER = None
        return redirect("/astronomy-site")
    return redirect("/astronomy-site/astronomy_sign_in")


@app.route("/astronomy-site/profile")
def profile():  # Функция изменения профиля.
    if MAIN_USER:
        form = EditingAccount()
        form.username.data = MAIN_USER.username
        form.age.data = MAIN_USER.age
        form.gender.data = MAIN_USER.gender
        form.password.data = MAIN_USER.hashed_password
        return render_template("profile.html", title="Profile", user=MAIN_USER, form=form)
    return redirect("/astronomy-site/astronomy_sign_in")


@app.route("/astronomy-site/astronomical-calendar")
def astro_calendar():  # Функция с созданием страницы астрономического календаря.
    if MAIN_USER:
        global_init("db/astronomy_site_users.db")
        session = create_session()
        events_dict = {}
        for info in session.query(Events).all():
            events_dict[info.date_of_event] = info.events.split(", ")
        return render_template("astronomy_calendar.html", title="Astronomical calendar",
                               events_dict=events_dict, user=MAIN_USER)
    return redirect("/astronomy-site/astronomy_sign_in")


@app.route("/astronomy-site/astronomy_sign_in", methods=['GET', 'POST'])
def astronomy_sign_in():  # Функция захода в чуществующий аккаунт.
    global MAIN_USER
    form = SignIn()
    if form.validate_on_submit():
        global_init("db/astronomy_site_users.db")
        session = create_session()
        user = session.query(User).filter(
            User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            MAIN_USER = user
            return redirect("/astronomy-site")
        else:
            return render_template("sign_in.html", form=form, message='Incorrect password.', title='Sign in')
    return render_template('sign_in.html', form=form, title='Sign in')


@app.route("/astronomy-site/astronomy_sign_up", methods=['GET', 'POST'])
def astronomy_sign_up():  # Функция регистрации пользователя.
    global MAIN_USER
    form = SignUp()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('sign_up.html', form=form, message="Passwords don't match.", title='Sign up')
        global_init("db/astronomy_site_users.db")
        session = create_session()
        if session.query(User).filter(User.username == form.username.data).first():
            return render_template("sign_up.html", form=form, message='This user have already registrared.',
                                   title='Sign up')
        if session.query(User).filter(User.email == form.email.data).first():
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
        session.add(user)
        session.commit()
        MAIN_USER = session.query(User).filter(User.username == form.username.data).first()
        return redirect("/astronomy-site")
    return render_template('sign_up.html', form=form, title='Sign up')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
