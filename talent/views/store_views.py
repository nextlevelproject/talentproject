import os
from flask import Blueprint, render_template, redirect, request, current_app, url_for, flash, g
from datetime import datetime
from werkzeug.utils import secure_filename

from talent import db
from talent.models import Store, User
from talent.forms import StoreForm

bp = Blueprint('store', __name__, url_prefix='/store')


# 상품 목록
@bp.route('/')
def _list():
    page = request.args.get('page', default=1, type=int)
    kw = request.args.get('kw', default='', type=str)

    store_list = Store.query.order_by(Store.create_date.desc())

    if kw:
        search = f'%%{kw}%%'
        store_list = store_list.join(User).filter(
            Store.title.ilike(search) |
            Store.content.ilike(search) |
            User.username.ilike(search)
        ).distinct()

    store_list = store_list.paginate(page=page, per_page=10)
    return render_template('store/store_list.html', store_list=store_list, page=page, kw=kw)


@bp.route('/detail/<int:store_id>')
def detail(store_id):
    form = StoreForm()
    store = Store.query.get_or_404(store_id)
    return render_template('store/store_detail.html', store=store, form=form)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if g.user is None or not g.user.is_expert:
        flash("전문가만 상품을 등록할 수 있습니다.", "warning")
        return redirect(url_for("store._list"))

    form = StoreForm()
    if request.method == 'POST' and form.validate_on_submit():

        # ✅ 이미지가 없으면 에러 처리
        if not form.image.data:
            flash("이미지는 필수입니다.", "danger")
            return render_template("store/store_form.html", form=form)

        image_file = form.image.data
        image_path = None

        if image_file:
            today = datetime.now().strftime('%Y%m%d')
            upload_folder = os.path.join(current_app.root_path, 'static/uploads', today)
            os.makedirs(upload_folder, exist_ok=True)

            # 파일명 중복 방지 (시간 붙이는 방식)
            filename = secure_filename(image_file.filename)
            timestamp = datetime.now().strftime("%H%M%S")
            new_filename = f"{timestamp}_{filename}"

            file_path = os.path.join(upload_folder, new_filename)
            image_file.save(file_path)

            image_path = f'uploads/{today}/{new_filename}'

        store = Store(
            title=form.title.data,
            content=form.content.data,
            price=form.price.data,
            create_date=datetime.now(),
            edit_date=datetime.now(),
            owner_id=g.user.id,
            image_path=image_path
        )
        db.session.add(store)
        db.session.commit()
        return redirect(url_for('store._list'))

    return render_template('store/store_form.html', form=form)



@bp.route('/edit/<int:store_id>', methods=['GET', 'POST'])
def edit(store_id):
    store = Store.query.get_or_404(store_id)

    # 작성자 체크
    if g.user is None or g.user.id != store.owner_id:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('store._list'))

    form = StoreForm(obj=store)
    if request.method == 'POST' and form.validate_on_submit():
        store.title = form.title.data
        store.content = form.content.data
        store.price = form.price.data
        store.edit_date = datetime.now()

        # ✅ 이미지 수정 로직 (선택적)
        if form.image.data:   # 새 이미지를 업로드한 경우에만 실행
            image_file = form.image.data
            today = datetime.now().strftime('%Y%m%d')
            upload_folder = os.path.join(current_app.root_path, 'static/uploads', today)
            os.makedirs(upload_folder, exist_ok=True)

            # 파일명 중복 방지: 시간 붙이기 방식
            filename = secure_filename(image_file.filename)
            timestamp = datetime.now().strftime("%H%M%S")
            new_filename = f"{timestamp}_{filename}"

            file_path = os.path.join(upload_folder, new_filename)
            image_file.save(file_path)

            # DB에 새로운 경로 반영
            store.image_path = f'uploads/{today}/{new_filename}'

        # 이미지 안 올리면 → store.image_path는 그대로 유지
        db.session.commit()
        return redirect(url_for('store.detail', store_id=store.id))

    return render_template('store/store_form.html', form=form)




@bp.route('/delete/<int:store_id>')
def delete(store_id):
    store = Store.query.get_or_404(store_id)

    if g.user is None or g.user.id != store.owner_id:
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('store.detail', store_id=store.id))

    db.session.delete(store)
    db.session.commit()
    flash('삭제되었습니다.')
    return redirect(url_for('store._list'))
