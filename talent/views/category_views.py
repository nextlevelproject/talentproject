from flask import Blueprint, render_template

bp = Blueprint('category', __name__, url_prefix='/category')

@bp.route('/move')
def move():
    return render_template('category/move.html')

@bp.route('/cleaning')
def cleaning():
    return render_template('category/cleaning.html')

@bp.route('/installation')
def installation():
    return render_template('category/installation.html')

@bp.route('/repair')
def repair():
    return render_template('category/repair.html')

@bp.route('/interior')
def interior():
    return render_template('category/interior.html')

@bp.route('/event')
def event():
    return render_template('category/event.html')

@bp.route('/beauty')
def beauty():
    return render_template('category/beauty.html')

@bp.route('/fashion')
def fashion():
    return render_template('category/fashion.html')

@bp.route('/employment')
def employment():
    return render_template('category/employment.html')

@bp.route('/private_lesson')
def private_lesson():
    return render_template('category/private_lesson.html')

@bp.route('/hobby')
def hobby():
    return render_template('category/hobby.html')

@bp.route('/self-development')
def self_development():
    return render_template('category/self-development.html')

@bp.route('/pet')
def pet():
    return render_template('category/pet.html')

@bp.route('/psychology')
def psychology():
    return render_template('category/psychology.html')

@bp.route('/law')
def law():
    return render_template('category/law.html')

@bp.route('/car')
def car():
    return render_template('category/car.html')

@bp.route('/travel')
def travel():
    return render_template('category/travel.html')

@bp.route('/etc')
def etc():
    return render_template('category/etc.html')