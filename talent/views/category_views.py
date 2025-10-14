from flask import Blueprint, render_template, redirect, url_for

from talent.forms import MoveForm, CleaningForm, InstallForm, RepairForm, InteriorForm, \
    EventForm, BeautyForm, FashionForm, EmployForm, PriForm, HobbyForm, \
    PetForm, LawForm, CarForm, TravelForm, EtcForm


bp = Blueprint('category', __name__, url_prefix='/category')

@bp.route('/move')
def move():
    form = MoveForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/move.html', form=form)

@bp.route('/cleaning')
def cleaning():
    form = CleaningForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/cleaning.html', form=form)

@bp.route('/installation')
def installation():
    form = InstallForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/installation.html', form=form)

@bp.route('/repair')
def repair():
    form = RepairForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/repair.html', form=form)

@bp.route('/interior')
def interior():
    form = InteriorForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/interior.html', form=form)

@bp.route('/event')
def event():
    form = EventForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/event.html', form=form)

@bp.route('/beauty')
def beauty():
    form = BeautyForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/beauty.html', form=form)

@bp.route('/fashion')
def fashion():
    form = FashionForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/fashion.html', form=form)

@bp.route('/employment')
def employment():
    form = EmployForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/employment.html', form=form)
    return render_template('category/employment.html')

@bp.route('/private_lesson')
def private_lesson():
    form = PriForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/private_lesson.html', form=form)

@bp.route('/hobby')
def hobby():
    form = HobbyForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/hobby.html', form=form)

@bp.route('/pet')
def pet():
    form = PetForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/pet.html', form=form)

@bp.route('/law')
def law():
    form = LawForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/law.html', form=form)

@bp.route('/car')
def car():
    form = CarForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/car.html', form=form)

@bp.route('/travel')
def travel():
    form = TravelForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/travel.html', form=form)
    return render_template('category/travel.html')

@bp.route('/etc')
def etc():
    form = EtcForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('category/etc.html', form=form)