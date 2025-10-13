from flask import Blueprint, render_template

bp = Blueprint('category', __name__, url_prefix='/category')

@bp.route('/move')
def move():
    return render_template('category/move.html')