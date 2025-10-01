from flask import Blueprint, render_template

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    # templates/index.html 파일이 존재해야 함
    return render_template('index.html')
