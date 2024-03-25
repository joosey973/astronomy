from flask import Flask, render_template, redirect, url_for, make_response
from sign_in import SignIn
from sign_up import SignUp
from data.users import User
from data.db_session import global_init, create_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
MAIN_USER = None


@app.route("/astronomy-site")
def astronomy_site():
    return render_template("main_page.html", title="astronomy-site", user=MAIN_USER)


@app.route("/astronomy-site/solar_hypotheses")
def solar_hypotheses():
    if MAIN_USER:
        return render_template("solar_hypotheses.html", user=MAIN_USER)
    return redirect(url_for("astronomy_sign_in")) 


@app.route("/astronomy-site/logout")
def logout():
    global MAIN_USER
    if MAIN_USER:
        MAIN_USER = None
        return redirect(url_for("astronomy_site"))
    return redirect(url_for("astronomy_sign_in"))


@app.route("/astronomy-site/profile")
def profile():
    if MAIN_USER:
        return render_template("profile.html", title="Profile", user=MAIN_USER)
    return redirect(url_for("astronomy_sign_in"))


@app.route("/astronomy-site/astronomy_sign_in", methods=['GET', 'POST'])
def astronomy_sign_in():
    global MAIN_USER
    form = SignIn()
    if form.validate_on_submit():
        global_init("db/astronomy_site_users.db")
        session = create_session()
        user = session.query(User).filter(
            User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            MAIN_USER = user
            return redirect(url_for('astronomy_site'))
        else:
            return render_template("sign_in.html", form=form, message='Incorrect password.', title='Sign in')
    return render_template('sign_in.html', form=form, title='Sign in')


@app.route("/astronomy-site/astronomy_sign_up", methods=['GET', 'POST'])
def astronomy_sign_up():
    global MAIN_USER
    form = SignUp()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('sign_up.html', form=form, message="Passwords don't match.", title='Sign up')
        global_init("db/astronomy_site_users.db")
        session = create_session()
        if session.query(User).filter(User.username == form.username.data).first():
            return render_template("sign_up.html", form=form, message='This user have already registrared.', title='Sign up')
        user = User()
        user.username = form.username.data
        user.age = form.age.data
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        MAIN_USER = session.query(User).filter(User.username == form.username.data).first()
        return redirect(url_for("astronomy_site"))
    return render_template('sign_up.html', form=form, title='Sign up')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
