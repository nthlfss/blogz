  
from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:lcblog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


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
        # verify if fields are empty
        if len(post_title) == 0:
            titleError = "Field cannot be empty"
        if len(post_body) == 0:
            bodyError = "Field cannot be empty"
        # if no errors, add input to db
        if not titleError and not bodyError:
            new_post = Blog(title=post_title, body=post_body)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('index'))
        # else reload same page with error messages
        else:
            return render_template('newpost.html', pagetitle="Add A New Blog Entry", titleError=titleError, bodyError=bodyError, body=post_body, title=post_title)

    

    return render_template('newpost.html', pagetitle="Add A New Blog Entry")


if __name__ == '__main__':
    app.run()