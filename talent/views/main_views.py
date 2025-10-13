from flask import Blueprint, render_template
from sqlalchemy import func
from talent.models import Store, CommunityPost

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    like_count = func.count().label("like_count")

    s_posts = (Store.query.order_by(Store.views.desc(), Store.create_date.desc()).limit(3).all())
    c_posts = (CommunityPost.query.outerjoin(CommunityPost.likes).group_by(CommunityPost.id)
               .order_by(like_count.desc(), CommunityPost.create_date.desc()).limit(3).all())
    return render_template('main.html', s_posts=s_posts, c_posts=c_posts)
