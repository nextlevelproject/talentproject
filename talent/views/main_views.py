from flask import Blueprint, url_for, redirect

@bp.route('/')
def index():
    return redirect(url_for('main.html'))