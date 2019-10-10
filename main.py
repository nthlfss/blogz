  
from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lcblog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(500))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    pwhash = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pwhash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pwhash):
            session['username'] = username
            flash('Logged in')
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html', pagetitle="Log In")

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    # initialize error variables
    usernameError = ""
    passwordError = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        else:
            return "<h1> duplicate user</h1>"
    return render_template('signup.html', pagetitle="Sign Up")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/')
@app.route('/blog')
def index():
    entries = Blog.query.order_by(Blog.id.desc())
    return render_template('blog.html', pagetitle="Build A Blog!", entries=entries)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    # initialize error variables
    titleError = ""
    bodyError = ""

    if request.method == 'POST':
        # save user input into variables
        post_title = request.form['title']
        post_body = request.form['body']
        user = User.query.filter_by(id=1).first()
        # verify if fields are empty
        if len(post_title) == 0:
            titleError = "Field cannot be empty"
        if len(post_body) == 0:
            bodyError = "Field cannot be empty"
        # if no errors, add input to db
        if not titleError and not bodyError:
            new_post = Blog(title=post_title, body=post_body, owner=user)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('index'))
        # else reload same page with error messages
        else:
            return render_template('newpost.html', pagetitle="Add A New Blog Entry", titleError=titleError, bodyError=bodyError, body=post_body, title=post_title)
    return render_template('newpost.html', pagetitle="Add A New Blog Entry")
    
@app.route('/post/<int:id>')
def post(id):
    entry = Blog.query.get(id)
    return render_template('post.html', entry=entry, pagetitle=entry.title)


if __name__ == '__main__':
    app.run()