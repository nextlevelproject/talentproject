from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime
import os

from talent import db
from talent.models import Post, Comment, Like, CommentLike, User

bp = Blueprint('community', __name__, url_prefix='/community')

UPLOAD_FOLDER = os.path.join('static', 'uploads')

# Home / Community
@bp.route('/')
def home():
    posts = Post.query.order_by(Post.create_date.desc()).all()
    return render_template('community.html', posts=posts, active_tab='community')

# Create Post
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
            image.save(os.path.join(UPLOAD_FOLDER, filename))

        post = Post(title=title, content=content, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('community.home'))
    return render_template('create_post.html')

# Post Detail
@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST' and current_user.is_authenticated:
        comment_content = request.form.get('comment')
        if comment_content:
            comment = Comment(content=comment_content, post_id=post.id, author_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('community.post_detail', post_id=post.id))
    return render_template('post_detail.html', post=post)

# Likes
@bp.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = next((like for like in post.likes if like.user_id == current_user.id), None)
    if not existing_like:
        db.session.add(Like(user_id=current_user.id, post_id=post.id))
        db.session.commit()
    return redirect(url_for('community.post_detail', post_id=post.id))

@bp.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    existing_like = next((like for like in comment.likes if like.user_id == current_user.id), None)
    if not existing_like:
        db.session.add(CommentLike(user_id=current_user.id, comment_id=comment.id))
        db.session.commit()
    return redirect(url_for('community.post_detail', post_id=comment.post_id))
