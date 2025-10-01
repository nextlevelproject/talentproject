from flask import Blueprint, redirect, url_for

bp = Blueprint('store',__name__, url_prefix='/store')

@bp.route('/store')
def index():
    return redirect(url_for('store.index'))