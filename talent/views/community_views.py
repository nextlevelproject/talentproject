from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from talent.models import db, Post, Comment, Like  # ✅ fixed import

bp = Blueprint('community', __name__, url_prefix='/community')

@bp.route('/')
def community_list():
    posts = Post.query.order_by(Post.create_date.desc()).all()
    return render_template('community/community_list.html', posts=posts)

@bp.route('/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        if 'comment' in request.form:
            content = request.form['comment']
            if content:
                new_comment = Comment(content=content, post_id=post.id, author_id=current_user.id)
                db.session.add(new_comment)
                db.session.commit()
        elif 'like' in request.form:
            existing_like = Like.query.filter_by(post_id=post.id, user_id=current_user.id).first()
            if not existing_like:
                new_like = Like(post_id=post.id, user_id=current_user.id)
                db.session.add(new_like)
                db.session.commit()

        return redirect(url_for('community.post_detail', post_id=post.id))

    return render_template('community/post_detail.html', post=post)
