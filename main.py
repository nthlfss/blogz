  
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
    body = db.Column(db.String(500), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    pwhash = db.Column(db.String(120), nullable=False)
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pwhash = make_pw_hash(password)

# def to require login
@app.before_request
def require_login():
    # routes allowed to be viewed without login
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
            flash('Logged in', 'success')
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'danger')

    return render_template('login.html', pagetitle="Log In", pageLabel="LOG IN")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
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
            flash('New user registered', 'success')
            return redirect('/login')
        else:
            flash('User password incorrect, or user does not exist', 'danger')
    return render_template('signup.html', pagetitle="Sign Up", pageLabel="SIGN UP")

@app.route('/logout')
def logout():
    del session['username']
    flash('User has been logged out', 'warning')
    return redirect('/')

@app.route('/')
@app.route('/blog')
def allblog():
    user = User.query.filter_by(username=session['username']).first()
    entries = Blog.query.filter_by(owner=user).order_by(Blog.date_posted.desc())
    return render_template('blog.html', pagetitle="Blogz", entries=entries, user=user, pageLabel="RECENT POSTS")


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    # initialize error variables
    titleError = ""
    bodyError = ""

    if request.method == 'POST':
        # save user input into variables
        post_title = request.form['title']
        post_body = request.form['body']
        user = User.query.filter_by(username=session['username']).first()
        # verify if fields are empty
        if len(post_title) != 0 or len(post_body) != 0:
            new_post = Blog(title=post_title, body=post_body, owner=user)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog')
        # else reload same page with error messages
        else:
            flash('All fields required', 'danger')
    
    return render_template('newpost.html', pagetitle="Add A New Blog Entry", pageLabel="NEW POST")
    
@app.route('/post/<int:id>')
def post(id):
    entry = Blog.query.get(id)
    return render_template('post.html', entry=entry, pagetitle=entry.title, pageLabel=entry.title)


if __name__ == '__main__':
    app.run()