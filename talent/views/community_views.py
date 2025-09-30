from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///community.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ----------------- Models -----------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), default=datetime.utcnow)
    is_pro = db.Column(db.Boolean, default=False)
    image_filename = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('CommentLike', backref='comment', lazy=True)

    author = db.relationship('User', backref='comments')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# ----------------- Login -----------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ----------------- Home / Community -----------------
@app.route('/')
def home():
    posts = Post.query.order_by(Post.create_date.desc()).all()
    return render_template('community.html', posts=posts, active_tab='community')

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        is_pro = 'is_pro' in request.form
        image = request.files.get('image')
        filename = None
        if image:
            filename = f"{datetime.utcnow().timestamp()}_{image.filename}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        post = Post(title=title, content=content, is_pro=is_pro, image_filename=filename, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_post.html')

# ----------------- Post Detail -----------------
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST' and current_user.is_authenticated:
        comment_content = request.form.get('comment')
        if comment_content:
            comment = Comment(content=comment_content, post_id=post.id, author_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('post_detail', post_id=post.id))

    return render_template('post_detail.html', post=post)

# ----------------- Likes -----------------
@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = next((like for like in post.likes if like.user_id == current_user.id), None)
    if not existing_like:
        db.session.add(Like(user_id=current_user.id, post_id=post.id))
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post.id))

@app.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    existing_like = next((like for like in comment.likes if like.user_id == current_user.id), None)
    if not existing_like:
        db.session.add(CommentLike(user_id=current_user.id, comment_id=comment.id))
        db.session.commit()
    return redirect(url_for('post_detail', post_id=comment.post_id))

# ----------------- Pro Center -----------------
@app.route('/pro_center')
def pro_center():
    return "<h1>Pro Center Page (coming soon)</h1>"

# ----------------- Initialize -----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Add test user if not exists
        if not User.query.filter_by(username='test').first():
            db.session.add(User(username='test', password='1234'))
            db.session.commit()
    app.run(debug=True)
