from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Feedback
from forms import AddFeedbackForm, LoginForm, UserForm, DeleteForm



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route("/users/<username>")
def show_user(username):
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm()
    feedback = Feedback.query.all()
    return render_template('show_user.html', user=user, form=form, feedback=feedback)

@app.route('/register', methods=['GET', 'POST'])
def register_users():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username
        flash('Welcome! You successfully created your Account', 'success')
        return redirect(f"/users/{new_user.username}")
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}", 'info')
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password!']
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

    
@app.route('/logout', methods=['GET', 'POST'])
def logout_user():
    session.pop('username')
    flash("You have logged out.", 'info')
    return redirect('/')


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    user = User.query.get(username)
    if "username" in session:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash("You have deleted your account!", "danger")
        return redirect('/')
    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def feedback_add(username):
    user = User.query.get(username)
    form = AddFeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        usernames = session['username']

        new_feedback = Feedback.add_feedback(title, content, usernames)
        db.session.add(new_feedback)
        db.session.commit()
        flash("You have posted feedback!")
        return redirect(f"/users/{session['username']}")

    return render_template('/feedback.html', user=user, form=form)

        
@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def feedback_update(feedback_id):
    fb = Feedback.query.get(feedback_id)

    if "username" not in session or fb.username != session['username']:
        raise Unauthorized()

    form = AddFeedbackForm(obj=fb)
    
    if form.validate_on_submit():
        fb.title = form.title.data
        fb.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{fb.username}")

    return render_template('feedback_edit.html', fb=fb, form=form)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def feedback_delete(feedback_id):
    fb = Feedback.query.get(feedback_id)
    user = fb.username
    db.session.delete(fb)
    db.session.commit()
    return redirect(f"/users/{user}")
