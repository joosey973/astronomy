from flask import Flask, render_template, redirect, url_for, request
from scripts.sign_in import SignIn
from scripts.sign_up import SignUp
from scripts.new_password import NewPassword
from data.users import User
from data.data_base_session import data_base_init, new_session
from scripts.send_message_to_email import generate_code, send_email_with_switch_confirm
from data.events import Events
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from scripts.check_password import check_password
from scripts.events_parser import get_data_from_web_site
from scripts.records_form import RecordForm
from data.records import Records

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign_in"
app.config['SECRET_KEY'] = 'secret_key'
EMAIL = None
RESET_CODE = None
NEW_EMAIL = None
CODE = None
data_base_init("db/astronomy_site_users.db")


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
        user.profile_url = f"/astronomy-site/show_user_profile/{user.username}"
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
    return render_template("established_solar_hypotheses.html",
                           title='Well-established of formation of the Solar system hypotheses')


@app.route("/astronomy-site/show_user_profile/<string:username>")
@login_required
def show_user_profile(username):
    data_base_session = new_session()
    user = data_base_session.query(User).filter(User.username == username).first()
    return render_template("show_user_profile.html", user=user, title=f"{user.username}'s profile")


@app.route("/astronomy-site/your_hypotheses", methods=['POST', 'GET'])
@login_required
def your_hypotheses():
    if request.method == 'POST':
        try:
            if request.form['post_id']:
                return redirect(url_for("claim_to_the_post", post_id=request.form['post_id']))
        except Exception:
            if int(request.form['isedit']) < 0:
                return redirect(url_for("delete_post", post_id=request.form['isdelete']))
            else:
                return redirect(url_for("edit_post", post_id=request.form['isedit']))
    data_base_session = new_session()
    posts = data_base_session.query(Records).all()
    posts = sorted(posts, key=lambda x: x.created_date)
    users_and_records_dict = dict()
    for post in posts:
        user = data_base_session.query(User).filter(User.id == post.user_id).first()
        users_and_records_dict[post] = user
    return render_template("your_hypotheses.html", users_and_records_dict=users_and_records_dict,
                           title='Your hypotheses of formation of the Solar system')


@app.route("/astronomy-site/your_hypotheses/delete_post/<int:post_id>")
@login_required
def delete_post(post_id):
    data_base_session = new_session()
    post = data_base_session.query(Records).filter(Records.id == post_id).first()
    if not post:
        return render_template("no_such_record.html", title=f"Post {post_id}")
    user = data_base_session.query(User).filter(User.id == post.user_id).first()
    if user.username != current_user.username:
        return redirect(url_for("your_hypotheses"))
    data_base_session.delete(post)
    data_base_session.commit()
    return redirect(url_for("your_hypotheses"))


@app.route("/astronomy-site/your_hypotheses/edit_post/<int:post_id>", methods=['POST', 'GET'])
@login_required
def edit_post(post_id):
    data_base_session = new_session()
    post = data_base_session.query(Records).filter(Records.id == post_id).first()
    if not post:
        return render_template("no_such_record.html", title=f"Post {post_id}")
    user = data_base_session.query(User).filter(User.id == post.user_id).first()
    if user.username != current_user.username:
        return redirect(url_for("your_hypotheses"))
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        data_base_session.commit()
        return redirect(url_for("your_hypotheses"))
    return render_template("edit_post.html", title="Edit post", post=post)


@app.route("/astronomy-site/your_hypotheses/claim/<int:post_id>", methods=['GET', 'POST'])
@login_required
def claim_to_the_post(post_id):
    data_base_session = new_session()
    post = data_base_session.query(Records).filter(Records.id == post_id).first()
    if not post:
        return render_template("no_such_post.html", title=f"Post {post_id}")
    if post.user_id == current_user.id:
        return redirect(url_for("your_hypotheses"))
    if request.method == 'POST':
        post.count_of_claims += 1
        data_base_session.commit()
        return redirect(url_for("message_after_claim", **{"issended": True}))
    return render_template("claim.html", title="Claim", post_id=post_id)
    # try:
    #     post = data_base_session.query(Records).filter(Records.id == post_id).first()
    # except Exception:
    #     return redirect(url_for("message_after_claim", **{"issended": True}))


@app.route("/astronomy-site/your_hypotheses/claim/message")
def message_after_claim():
    if request.args.get("issended"):
        return render_template("message_after_claim.html", title='Message After Claim')
    return redirect(url_for("your_hypotheses"))


@app.route("/astronomy-site/your_hypotheses/write_hypothesis", methods=['POST', 'GET'])
@login_required
def write_hypothesis():
    form = RecordForm()
    if form.validate_on_submit():
        data_base_session = new_session()
        record = Records()
        record.title = form.title.data
        record.content = form.content.data
        current_user.records.append(record)
        data_base_session.merge(current_user)
        data_base_session.commit()
        return redirect(url_for("your_hypotheses"))
    return render_template("write_hypothesis.html", title="Record addition", form=form)


@app.route("/astronomy-site/your_hypotheses/<int:record_id>")
def show_record(record_id):
    data_base_session = new_session()
    record = data_base_session.query(Records).filter(Records.id == record_id).first()
    try:
        user = data_base_session.query(User).filter(User.id == record.user_id).first()
    except Exception:
        return render_template("no_such_record.html", title=f'Post {record_id}')
    return render_template("show_post_by_id.html", title=f"Post {record_id}",
                           user=user, post=record)


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
    global EMAIL, RESET_CODE
    if request.method == 'POST':
        RESET_CODE = generate_code()
        EMAIL = request.form['email']
        send_email_with_switch_confirm(EMAIL, RESET_CODE)
        return redirect(url_for("password_reset_with_code"))
    return render_template("forgot_password.html", title='Forgot password')


@app.route("/astronomy-site/password_reset/code", methods=['GET', 'POST'])
def password_reset_with_code():
    global RESET_CODE
    if not EMAIL:
        return redirect(url_for("password_reset"))
    if request.method == 'POST':
        if request.form['email_send']:
            RESET_CODE = generate_code()
            send_email_with_switch_confirm(EMAIL, RESET_CODE)
        else:
            if request.form['code'] != RESET_CODE:
                return render_template("forgot_password_code.html", title='Code', message='Incorrect password.',
                                       EMAIL=EMAIL)
            return redirect(url_for("new_password"))
    return render_template("forgot_password_code.html", title='Code', EMAIL=EMAIL)


@app.route("/astronomy-site/password_reset/code/new_password", methods=['POST', 'GET'])
def new_password():
    global EMAIL, RESET_CODE
    if not EMAIL:
        return redirect(url_for("password_reset"))
    form = NewPassword()
    if form.validate_on_submit():
        if request.form['password'] != form.repeat_password.data:
            return render_template("new_password.html", title='New password', message="Passwords don't match",
                                   form=form)
        if check_password(request.form['password']):
            return render_template("new_password.html", title='New password', message="Weak password.", form=form)
        data_base_session = new_session()
        user = data_base_session.query(User).filter(User.email == EMAIL).first()
        user.set_password(request.form['password'])
        data_base_session.commit()
        EMAIL = None
        RESET_CODE = None
        return redirect(url_for("astronomy_site"))
    return render_template("new_password.html", title='New password', form=form)


# @app.route("/astronomy-site/password_reset", methods=['GET', 'POST'])
# def password_reset():
#     global ISSENDED, EMAIL
    # form = PasswordReset()
#     if form.validate_on_submit():
#         session = new_session()
#         user = session.query(User).filter(User.email == form.email.data).first()
#         if user:
#             send_email_with_reset(user.email)
#             ISSENDED = True
#             EMAIL = user.email
#             return redirect(url_for("revieve_message_page"))
#         return render_template("forgot.html", form=form, title="Reset password", message="There is no such mail.")
#     return render_template("forgot.html", form=form, title="Reset password")


# @app.route("/astronomy-site/reset_password/revieve_message")
# def revieve_message_page():
#     if ISSENDED:
#         return render_template("message.html", title="Recieve Message")
#     return redirect(url_for("password_reset"))
# @ app.route("/astronomy-site/reset_password/revieve_message/new_password", methods=['GET', 'POST'])
# def set_new_password():
#     global ISSENDED, EMAIL
#     if not ISSENDED:
#         return redirect(url_for("password_reset"))
#     form = NewPassword()
#     if form.validate_on_submit():
#         if request.form['password'] == form.password_repeat.data:
#             if check_password(form.password_repeat.data):
#                 return render_template("new_password.html", form=form, message="Weak password.", title='New password')
#             data_base_session = new_session()
#             user = data_base_session.query(User).filter(User.email == EMAIL).first()
#             if user.check_password(form.password.data):
#                 return render_template("new_password.html", form=form, message="This password is already taken.",
#                                        title="New password")
#             user.set_password(form.password.data)
#             data_base_session.commit()
#             data_base_session.close()
#             ISSENDED = False
#             EMAIL = None
#             return redirect(url_for("sign_in"))
#         return render_template("new_password.html", form=form, message="Passwords don't match.", title="New password")
#     return render_template("new_password.html", form=form, title="New password")


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


@ app.route("/astronomy-site/profile/confirm_email_change", methods=['POST', 'GET'])
@ login_required
def confirm_email_with_code():
    global NEW_EMAIL, CODE
    if not NEW_EMAIL:
        return redirect(url_for("profile"))
    if request.method == 'POST':
        if request.form['email_send']:
            CODE = generate_code()
            send_email_with_switch_confirm(NEW_EMAIL, CODE)
        else:
            if request.form['code'] != CODE:
                return render_template("profile_with_code.html", message='Incorrect code.',
                                       title='Confirm email change')
            data_base_session = new_session()
            user = data_base_session.query(User).filter(User.username == current_user.username).first()
            user.email = NEW_EMAIL
            data_base_session.commit()
            NEW_EMAIL = None
            CODE = None
            return redirect(url_for("profile"))
    return render_template("profile_with_code.html", title='Confirm email change')


if __name__ == "__main__":
    app.run(host="0.0.0.0")
