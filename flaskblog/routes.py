import datetime
import functools
from flask import render_template, url_for, flash, redirect, request, session, abort
from flaskblog import app, bcrypt, db
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post, Comment
from flask_login import login_required, current_user


from pymodm.errors import ValidationError
from pymongo.errors import DuplicateKeyError

from bson.objectid import ObjectId
def human_date(value, format="%B %d at %I:%M %p"):
    """Format a datetime object to be human-readable in a template."""
    return value.strftime(format)
app.jinja_env.filters['human_date'] = human_date


def logged_in(func):
    """Decorator that redirects to login page if a user is not logged in."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper



@app.route("/")
@app.route("/home")
def home():
    post_list = db.db.post
    posts = post_list.find()
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
	return render_template('about.html', title='About')



@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = db.db.user
        new_user = users.find_one({'_id': request.form['email'] })
        if new_user and bcrypt.check_password_hash(new_user['password'], request.form['password']):
            session['logged_in'] = True
            session['_id'] = request.form['email']
            session['username'] = new_user['username']
            flash('Login Successful. Welcome' + session['username'], 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        User(email=request.form['email'], username=request.form['username'], password=hashed_password).save()
        flash(f'Account Created! You may now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/account", methods=['GET', 'POST'])
@logged_in
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        users = db.db.user
        users.update({'username': session['username'] }, 
            {'$set': {'username': request.form['username'], '_id': request.form['email']}}) 
        flash(f'Account Updated!', 'success')
        session['_id'] = request.form['email']
        session['username'] = request.form['username']
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = session['username']
        form.email.data = session['_id']
    # image_file = url_for('static', filename='profile_pics/' + .image_file)
    return render_template('account.html', title='Account', form=form)

@app.route('/posts/new', methods=['GET', 'POST'])
@logged_in
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post_date = datetime.datetime.now()
        Post(title=request.form['title'],
                     date=post_date,
                     body=request.form['body'],
                     author=session['username']).save()
        flash(f'Post Created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Create Post', form=form,
        legend='New Post')

@app.route('/posts/<post_id>', methods=['GET', 'POST'])
def get_post(post_id):
    post_list = db.db.post
    post = post_list.find_one({'_id': ObjectId(post_id)})
    return render_template('post.html', post=post)


@app.route('/comments/new', methods=['POST'])
def new_comment():
    post_id = ObjectId(request.form['post_id'])
    try:
        post = Post.objects.get({'_id': post_id})
    except Post.DoesNotExist:
        flash('No post with id: %s' % post_id)
        return redirect(url_for('index'))
    comment = Comment(
        author=request.form['author'],
        date=datetime.datetime.now(),
        body=request.form['content'])
    post.comments.append(comment)
    try:
        post.save()
    except ValidationError as e:
        post.comments.pop()
        comment_errors = e.message['comments'][-1]
        return render_template('post.html', post=post, errors=comment_errors)
    flash('Comment saved successfully.')
    return render_template('post.html', post=post)
