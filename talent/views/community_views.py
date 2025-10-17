from flask import Blueprint, render_template, request, redirect, url_for, current_app, g, flash
from flask_login import current_user
from datetime import datetime, timedelta
import pytz
import os

from talent import db
from talent.models import CommunityPost, Comment, Like, CommentLike, User

bp = Blueprint('community', __name__, url_prefix='/community')

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


def get_active_user():
    """
    Bridge helper — returns the logged-in user regardless of
    whether the system uses Flask-Login (current_user)
    or legacy g.user/session system.
    """
    if getattr(current_user, "is_authenticated", False):
        return current_user
    return getattr(g, "user", None)


@bp.route('/')
@bp.route('/category/<string:category_name>')
def home(category_name=None):
    if category_name:
        posts = CommunityPost.query.filter_by(category=category_name).order_by(CommunityPost.create_date.desc()).all()
    else:
        posts = CommunityPost.query.order_by(CommunityPost.create_date.desc()).all()

    hot_picks = CommunityPost.query.filter(CommunityPost.is_pro == True).limit(5).all()
    return render_template(
        '/community/community.html',
        posts=posts,
        hot_posts=hot_picks,
        active_tab='community',
        human_readable_time=human_readable_time,
        selected_category=category_name
    )


@bp.route('/create_post', methods=['GET', 'POST'])
def create_post():
    user = get_active_user()  # could be None

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category')
        is_pro = 'is_pro' in request.form
        image = request.files.get('image')

        filename = None
        if image:
            filename = f"{datetime.utcnow().timestamp()}_{image.filename}"
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        post = CommunityPost(
            title=title,
            content=content,
            category=category,
            is_pro=is_pro,
            image_filename=filename,
            user_id=user.id if user else None  # allow guest posts
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('community.home'))

    return render_template('community/create_post.html', user=user)


@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    user = get_active_user()

    if request.method == 'POST' and user:
        comment_content = request.form.get('comment')
        if comment_content:
            comment = Comment(
                content=comment_content,
                post_id=post.id,
                user_id=user.id,
                author_id=user.id,  # <- this fixes the NOT NULL error
                create_date=datetime.utcnow()
            )
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('community.post_detail', post_id=post.id))

    return render_template(
        'community/post_detail.html',
        post=post,
        human_readable_time=human_readable_time,
        user=user
    )

@bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    user = get_active_user()
    comment = Comment.query.get_or_404(comment_id)

    # Only allow the author to delete
    if not user or comment.user_id != user.id:
        flash("삭제 권한이 없습니다.", "danger")
        return redirect(url_for('community.post_detail', post_id=comment.post_id))

    db.session.delete(comment)
    db.session.commit()
    flash("댓글이 삭제되었습니다.", "success")
    return redirect(url_for('community.post_detail', post_id=comment.post_id))

@bp.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    user = get_active_user()
    if not user:
        flash("로그인이 필요합니다.", "warning")
        return redirect(url_for('auth.login'))

    post = CommunityPost.query.get_or_404(post_id)
    existing_like = next((like for like in post.likes if like.user_id == user.id), None)
    if not existing_like:
        db.session.add(Like(user_id=user.id, post_id=post.id))
        db.session.commit()
    return redirect(url_for('community.post_detail', post_id=post.id))


@bp.route('/like_comment/<int:comment_id>', methods=['POST'])
def like_comment(comment_id):
    user = get_active_user()
    if not user:
        flash("로그인이 필요합니다.", "warning")
        return redirect(url_for('auth.login'))

    comment = Comment.query.get_or_404(comment_id)
    existing_like = next((like for like in comment.likes if like.user_id == user.id), None)
    if not existing_like:
        db.session.add(CommentLike(user_id=user.id, comment_id=comment.id))
        db.session.commit()
    return redirect(url_for('community.post_detail', post_id=comment.post_id))


@bp.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    user = get_active_user()

    # Only allow the author (or guest owner) to delete
    if post.user_id != (user.id if user else None):
        flash("You do not have permission to delete this post.", "danger")
        return redirect(url_for('community.home'))

    # Delete the post
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully.", "success")
    return redirect(url_for('community.home'))

    return render_template('community/edit_post.html', post=post)

@bp.route('/post/<int:post_id>/comment', methods=['POST'])
def create_comment(post_id):
    content = request.form['content']
    parent_id = request.form.get('parent_id')  # None if top-level comment
    comment = Comment(content=content, post_id=post_id, author_id=current_user.id, user_id=current_user.id, parent_id=parent_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('community_views.post_detail', post_id=post_id))

@bp.route('/pro_center')
def pro_center():
    return "<h1>Pro Center Page (coming soon)</h1>"
