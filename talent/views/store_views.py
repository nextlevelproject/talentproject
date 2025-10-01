import os
from flask import Blueprint, render_template, request, current_app, url_for, g, flash
from datetime import datetime

from werkzeug.utils import secure_filename, redirect

from talent import db
from talent.models import Store
from talent.forms import StoreForm
from talent.views.auth_views import login_required

bp = Blueprint('store',__name__, url_prefix='/store')

@bp.route('/list')
def _list():
    page = request.args.get('page', default=1, type=int)
    # kw = request.args.get('kw', default='', type=str)
    store_list = Store.query.order_by(Store.create_date.desc())
    # if kw:
    #     search = f'%%{kw}%%'
    #     sub_query = db.session.query(Store.user_id, Store.title, Store.content) \ #, User.userid)

    store_list = store_list.paginate(page=page, per_page=10)
    return render_template('store/store_list.html')

@bp.route('/store/detail/<int:store_id>')
def store_detail(store_id):
    form = StoreForm()
    store = Store.query.get_or_404(store_id)
    return render_template('store/detail.html', store=store, form=form)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StoreForm()
    if request.method == 'POST':
        image_file = form.image.data
        today = datetime.now().strftime('%Y%m%d')
        upload_folder = os.path.join(current_app.root_path, 'static/store_uploads', today)
        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(image_file.filename)
        file_path = os.path.join(upload_folder, filename)
        image_file.save(file_path)

        image_path = f'static/store_uploads/{filename}'

        store = Store(title=form.title.data,
                      content=form.content.data,
                      create_date=datetime.now(),
                      user_id=g.user.id,
                      image_path=image_path)
        db.session.add(store)
        db.session.commit()
    return render_template('store/store_list.html')

@bp.route('/edit/<int:store_id>', methods=['GET', 'POST'])
@login_required
def edit(store_id):
    store = Store.query.get_or_404(store_id)
    if g.user != store.user:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('store.index'))
    if request.method == 'POST':
        form = StoreForm()
        if form.validate_on_submit():
            form.populate_obj(store)
            store.edit_date = datetime.now()
            db.session.commit()
            return redirect(url_for('store.index'))
    else:
        form = StoreForm(obj=store)
    return render_template('store/store_form.html', form=form)

@bp.route('/delete/<int:store_id>')
@login_required
def delete(store_id):
    store = Store.query.get_or_404(store_id)
    if g.user != store.user:
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('store.detail'))
    else:
        db.session.delete(store)
        db.session.commit()
    return redirect(url_for('store.index'))