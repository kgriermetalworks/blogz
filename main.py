from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        self.pub_date = datetime.utcnow()


    def __repr__(self):
        return '<Blog %r>' % self.title


@app.route('/blog', methods=['GET'])
def blog():
    #This query will list all rows in the table in DESC order. shows most recent post --> oldest
    blogs = Blog.query.order_by(Blog.pub_date.desc()).all()

    #GET blog Id so link will fuction to individual pages
    blog_id = request.args.get('id')
    if (blog_id):
        entry = Blog.query.get(blog_id)
        return render_template('entry.html', title="Blog Entry", entry=entry)

    return render_template('blog.html', blogs=blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    bt_error = ''
    bb_error = ''

    #Validate the form so user doesnt publish an empty title or body
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        
        if blog_title == '':
            bt_error = "Oopsie! you forgot a title for your blog post."
            
        if blog_body == '':
            bb_error = "Whoa! You cant have a blog post without content."

        #NO errors we commit and send user to new_post's individual page  
        else:
            new_post = Blog(blog_title, blog_body)
            db.session.add(new_post)
            db.session.commit()

            url = "/blog?id=" + str(new_post.id)
            return redirect(url)

    return render_template('newpost.html', bt_error=bt_error, bb_error=bb_error)

@app.route('/', methods=['POST', 'GET'])
def index():
    #Send user immediately to blog main page
    return redirect('/blog')


if __name__ == '__main__':
    app.run()