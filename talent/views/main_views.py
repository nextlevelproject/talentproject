from flask import Blueprint, redirect, url_for, session, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template(url_for('index.html'))
