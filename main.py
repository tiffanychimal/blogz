from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), nullable=False)

    def __init__(self, name):
        self.title = name

blogs = []

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog = request.form['title']
        blog.append(title)

    blogs = Blog.query.all()
    return render_template('newpost.html',title="New Blog Post")

if __name__ == '__main__':
    app.run()