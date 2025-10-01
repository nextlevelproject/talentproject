# community_views.py
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
from talent import db
from talent.models import User, Post, Comment, Like, CommentLike
from datetime import datetime, timedelta
import pytz
import os

bp = Blueprint('community_views', __name__)

# ----------------- Timezone -----------------
KST = pytz.timezone('Asia/Seoul')

def human_readable_time(post_time):
    post_local = post_time.replace(tzinfo=pytz.utc).astimezone(KST)
    now_local = datetime.now(KST)
    diff = now_local - post_local

    if diff < timedelta(minutes=1):
        return "방금 전"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() // 60)
        return f"{minutes}분전"
    elif diff < timedelta(hours=24):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours}시간전"
    elif diff < timedelta(days=2):
        return "어제"
    else:
        return post_local.strftime("%Y-%m-%d")

# ----------------- Routes -----------------

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('community_views.home'))
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('community_views.login'))


@bp.route('/')
def home():
    posts = Post.query.order_by(Post.create_date.desc()).all()
    hot_picks = Post.query.filter(Post.is_pro==True).limit(5).all()
    return render_template('community.html',
                           posts=posts,
                           hot_picks=hot_picks,
                           active_tab='community',
                           human_readable_time=human_readable_time,
                           current_user=current_user)


@bp.route('/create_post', methods=['GET', 'POST'])
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
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        post = Post(title=title,
                    content=content,
                    is_pro=is_pro,
                    image_filename=filename,
                    author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('community_views.home'))
    return render_template('create_post.html')


@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST' and current_user.is_authenticated:
        comment_content = request.form.get('comment')
        if comment_content:
            comment = Comment(content=comment_content,
                              post_id=post.id,
                              author_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('community_views.post_detail', post_id=post.id))
    return render_template('post_detail.html',
                           post=post,
                           human_readable_time=human_readable_time)


@bp.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = next((like for like in post.likes if like.user_id == current_user.id), None)
    if not existing_like:
        db.session.add(Like(user_id=current_user.id, post_id=post.id))
        db.session.commit()
    return redirect(url_for('community_views.post_detail', post_id=post.id))


@bp.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    existing_like = next((like for like in comment.likes if like.user_id == current_user.id), None)
    if not existing_like:
        db.session.add(CommentLike(user_id=current_user.id, comment_id=comment.id))
        db.session.commit()
    return redirect(url_for('community_views.post_detail', post_id=comment.post_id))


@bp.route('/pro_center')
def pro_center():
    return "<h1>Pro Center Page (coming soon)</h1>"
