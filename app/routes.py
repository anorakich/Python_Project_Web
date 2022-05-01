from datetime import *
from flask import render_template, redirect, url_for, request
from app.init import app
from app.forms import LoginForm, RegisterForm, PostForm
from app.models import User, Post
from flask_login import current_user, login_user, logout_user, login_required
from app.init import db
import functools


def sortPots(posts):
    def compare(post1, post2):
        if post1.date_created < post2.date_created:
            return -1
        if post1.date_created > post2.date_created:
            return 1
        return 0

    posts.sort(key=functools.cmp_to_key(compare), reverse=True)


@app.route('/')
@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    followed_to = current_user.followed
    posts = []
    for followed_to_user in followed_to:
        posts.extend(Post.query.filter_by(author=followed_to_user).all())
    sortPots(posts)
    return render_template('index.html', user=current_user, posts=posts)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/user/<username>', methods=['POST', 'GET'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(text=form.text.data, author_id=current_user.id, date_created=datetime.utcnow())
        db.session.add(post)
        db.session.commit()
    posts = Post.query.filter_by(author=user).all()
    sortPots(posts)
    return render_template('user.html', user=user, posts=posts, form=form,
                           subscribed=(current_user.followed.count(user) == 1))


@app.route('/globalNews', methods=["POST", "GET"])
@login_required
def globalNews():
    posts = Post.query.all()
    sortPots(posts)
    return render_template('globalNews.html', posts=posts)


@app.route('/subscribe/<username>')
def subscribe(username):
    user = User.query.filter_by(username=username).first()
    if current_user.followed.count(user) == 0:
        current_user.followed.append(user)
    db.session.commit()
    return redirect(url_for('user', username=username))


@app.route('/unsubscribe/<username>')
def unsubscribe(username):
    user = User.query.filter_by(username=username).first()
    if current_user.followed.count(user) == 1:
        current_user.followed.remove(user)
    db.session.commit()
    return redirect(url_for('user', username=username))


@app.route('/search', methods=['POST', 'GET'])
def search():
    if User.query.filter_by(username = request.form.get("username")).count() == 1:
        return redirect(url_for('user', username=request.form.get("username")))
    return redirect(url_for("page_not_found"))

@app.route('/page_not_found')
def page_not_found():
    return ("404 error page not found")