from flask import render_template  # invokes the Jinja2 template engine (part of Flask framework), takes a template filename and a variable list of template arguments and returns the same template withe placeholders replaced by the actual values.
from flask import flash, redirect, request, url_for, g
from urllib.parse import urlparse
from app import app #, db
from abstractions.database import db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, TextInput, ButtonInput
from flask_login import current_user, login_user, logout_user, login_required  # Used to implement real login view function now that there is an actual db.
from app.models import User, Post
from datetime import datetime
from app.email import send_password_reset_email
from flask_babel import _, get_locale
from googlesearch import search
import requests
import json


# In Flask, handlers for the app routes are written as python functions (=view functions).

# When a web browser requests either of these URLs, Flask is going to invoke this function and pass the returned value of it back to the browser as a response.
@app.route('/', methods=['GET', 'POST'])  # The `route()` decorator binds a function of a URL, the methods argument tells Flask that this view functions accepts `GET` and `POST` requests (default is `GET`).
@app.route('/index', methods=['GET', 'POST'])  # `GET` requests return info to the client (web browser). `POST` requests are used when the client submits form data to the server.
@login_required  # If the user is not logged in then it will redirected to unauthorized_handler
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # If user is already logged in there is no need to direct them to the login page
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data) #, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User %(username)s not found.', username=username)
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following %(username)s.', username=username)
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page,       app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return(url_for('idex'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
#
#
#@app.route('/delete_post/<post_id>/', methods=('GET', 'POST'))
#@login_required
#def delete_post(post_id):
#    post_id = Post.query.filter_by(id=Post.id).first_or_404()
#    db.session.delete(post_id)
#    db.session.commit()
#    return redirect(url_for('index'))


@app.route('/posts/<int:id>')
#@login_required
def show(id):
    return render_template("_post.html", post=Post.query.get(id), pid=id )


@app.route('/delete_post/<int:id>', methods=('GET', 'POST'))
@login_required
def delete_post(id):
    id = Post.query.get(id)
    if id is None:
        flash('Post not found.')
        return redirect(url_for('index'))

    db.session.delete(id)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('index'))


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


@app.route('/AI_API', methods=['GET', 'POST'])
def AI_API():
    text = TextInput()
    if text.validate_on_submit():
        query = text.text.data
        #return query
        results = []
        for i in search(query, tld='com', lang='en', num=10, start=0, stop=10, pause=2):
            results.append(i)
            flash(i)
    return render_template('text_field.html', form=text)


@app.route('/experimentation', methods=['GET', 'POST'])
def experimentation():

    exp_name = "migraine"
    intervention = requests.get(f"https://yg9r9w.deta.dev/experiments/{exp_name}/get_intervention")
    button = ButtonInput()
    #experiment_name = requests.get("https://yg9r9w.deta.dev/experiments/{experiment_name}")

    if button.validate_on_submit():

        if button.yes_button.data:
            outcome = 1
        else:
            outcome = 0


        json = {
                "experiment_name": exp_name,
                "arm_name": str(intervention.json()),
                "outcome": outcome,
            "accept": "application/json", "Content-Type": "application/json" }


        response = requests.post(f"https://yg9r9w.deta.dev/experiments/update", json=json)
        return str(button.yes_button.data)
        #f'you just took: {str(intervention.json())}' #str(intervention.json())#strstr(response.status_code)#payload#intervention.text

    return render_template('experimentation.html', intervention=intervention.text, form=button)



#
#    if <post comes through>:
#        payload = {
#              "experiment_name": "migraine",
#              "arm_name": intervention,
#              "outcome": <post button press, 0 or 1>
#            }
#            requests.post(<url>, params = payload)
#            return 'thanks for your feedback!'
#
