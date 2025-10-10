from flask import Blueprint, render_template

from ..models import CommunityPost

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    posts = CommunityPost.query.order_by(CommunityPost.create_date.desc()).limit(3).all()
    return render_template('main.html')
