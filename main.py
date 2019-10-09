  
from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lcblog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/')
@app.route('/blog')
def index():
    entries = Blog.query.order_by(Blog.id.desc())
    return render_template('blog.html', pagetitle="Build A Blog!", entries=entries)

@app.route('/signup')
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('index.html')
    return render_template('signup.html', pagetitle="Sign Up")

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