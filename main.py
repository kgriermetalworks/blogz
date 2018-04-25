from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogger@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) #grabbing id from the User clss

    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        self.pub_date = datetime.utcnow()
        

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(20))
    blogs =  db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                flash('welcome back, '+user.username)
                return redirect("/newpost")
        flash('bad username or password')
        return redirect("/login")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash('yikes! "' + username + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/newpost")
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog():
    #This query will list all rows in the table in DESC order. shows most recent post --> oldest
    all_blogs = Blog.query.order_by(Blog.pub_date.desc()).all()
    print('======================================', all_blogs)
    
    #GET blog Id so link will fuction to individual pages
    blog_id = request.args.get('id')
    if (blog_id):
        entry = Blog.query.get(blog_id)
        return render_template('entry.html', title="Blog Entry", entry=entry)

    return render_template('blog.html', all_blogs=all_blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    bt_error = ''
    bb_error = ''

    #Validate the form so user doesnt publish an empty title or body
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        
        if blog_title == '':
            bt_error = "Oopsie! you forgot a title for your blog post."
        if blog_body == '':
            bb_error = "Whoa! You cant have a blog post without content."

        if bt_error or bb_error:
            return render_template('newpost.html', bt_error=bt_error, bb_error=bb_error, blog_title=blog_title, blog_body=blog_body)

        #NO errors we commit and send user to new_post's individual page  
        else:
            usr = User.query.filter_by(username=session['user']).first()
            new_post = Blog(blog_title, blog_body, usr)
            db.session.add(new_post)
            db.session.commit()

            url = "/blog?id=" + str(new_post.id)
            return redirect(url)

    return render_template('newpost.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    #Send user immediately to blog main page
    return redirect('/blog')

endpoints_without_login = ['signup', 'login', 'static', 'blog', 'index']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")

app.secret_key = 'A0Zr98j/3yX R~X!!!!gtSD78jmN]LWX/,?RU'


if __name__ == '__main__':
    app.run()
