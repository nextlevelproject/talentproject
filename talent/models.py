# talent/models.py
from . import db
from datetime import datetime
from flask_login import UserMixin

# USER
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    # legacy login id (keep for compatibility)
    userid = db.Column(db.String(150), unique=True, nullable=False)

    # Add a "username" column which templates expect (you can set it from userid or name)
    username = db.Column(db.String(150), unique=False, nullable=True)

    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    tel_number = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    is_expert = db.Column(db.Boolean, default=False)
    service = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    social_id = db.Column(db.String(200), nullable=True)
    social_type = db.Column(db.String(20), nullable=True)

    # avatar that templates reference (fallback to default.png if null)
    avatar = db.Column(db.String(255), nullable=True)

    # optional helper property for templates if username isn't set
    @property
    def display_name(self):
        return self.username or self.name or self.userid or "Unknown"


# STORE
class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    create_date = db.Column(db.DateTime, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship('User', backref=db.backref('store'))
    edit_date = db.Column(db.DateTime, nullable=False)
    image_path = db.Column(db.String(120), nullable=False)
    views = db.Column(db.Integer, default=0)


# COMMUNITY
class CommunityPost(db.Model):
    __tablename__ = "community_post"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    is_pro = db.Column(db.Boolean, default=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Main author reference (used in all new code)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Backwards-compatible user_id for legacy views/code
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Relationship that templates expect: post.user
    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        backref=db.backref('posts', lazy='dynamic')
    )

    # Relationships for likes/comments
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy=True,
        cascade="all, delete-orphan"
    )
    likes = db.relationship(
        'Like',
        backref='post',
        lazy=True,
        cascade="all, delete-orphan"
    )

    # Image filename (templates reference post.image_filename)
    image_filename = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<CommunityPost {self.title} by author {self.author_id}>"

class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('comments', lazy='dynamic'))

    likes = db.relationship(
        'CommentLike',
        backref='comment',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class CommentLike(db.Model):
    __tablename__ = 'comment_like'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), nullable=False)
