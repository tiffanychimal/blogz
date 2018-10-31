from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'string'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))
    created = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title 
        self.body = body
        self.created = datetime.utcnow()
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login(): 
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/newpost')
        else: 
            flash('User password incorrect, or user does not exist', 'error') 
            return redirect('/login')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register(): 
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user's data - check user signup

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/blog')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title='Home', users=users)

@app.route('/blog', methods=['GET'])
def blog():
    if request.args.get("blog"):
        blog = Blog.query.get(request.args.get("blog"))
        return render_template('blogpost.html', blog=blog)

    if request.args.get("user"):
        user_id = request.args.get('user') # return an int (1,2, 300)
        user = User.query.get(user_id)
        return render_template('SingleUser.html', user=user)   

    # get blogs from database
    blogs = Blog.query.all()
    # return template with blogs
    return render_template('blogs.html', blogs=blogs) 

# @app.route('/singleuser', methods=['POST', 'GET'])
# def showuser():
#     blog_name = request.form['title']
#     owner = User.query.filter_by(email=session['email']).first()
#     user_id = request.args.get('users')
#     blogs = Blog.query.filter_by(username=user_id).all()
#     return render_template('singleuser.html', users=users, blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    return render_template('newpost.html')

@app.route('/validate-new-post', methods=['POST'])
def validate_new_post():

    title = request.form['title']
    body = request.form['body']
    
    title_error = ''
    body_error = ''

    if title == '':
        title_error = 'Please fill in the title'

    if body == '':
        body_error = 'Please fill in the blog post'

    if not title_error and not body_error:
        owner = User.query.filter_by(email=session['email']).first()
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('blogpost.html', blog=new_blog)
    else:
        return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, body=body)

@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.completed = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run()