from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify, g
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
import jwt, re

from talent import db, mail
from talent.models import User
from talent.forms import (
    LoginForm, SignupForm, ExpertSignupForm, EditProfileForm,
    FindIdForm, FindPasswordForm, ResetPasswordForm, ChangePasswordForm
)

# 비밀번호 규칙: 영문+숫자+특수문자 8~20자
PASSWORD_RE = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,20}$')

bp = Blueprint('auth', __name__, url_prefix='/auth')

# ----------------- g.user 로드 -----------------
@bp.before_app_request
def load_logged_in_user():
    uid = session.get('user_id')
    g.user = User.query.get(uid) if uid else None

# ----------------- Auth guard -----------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요한 기능입니다.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ----------------- Login -----------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        userid = form.userid.data.strip()
        password = form.password.data or ''
        user = User.query.filter_by(userid=userid).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            session['is_expert'] = bool(getattr(user, 'is_expert', False))
            flash(f'{user.userid}님, 로그인되었습니다.', 'success')
            return redirect(url_for('main.index'))
        flash('아이디 또는 비밀번호가 틀렸습니다.', 'danger')
    return render_template('auth/login.html', form=form)

# ----------------- Logout -----------------
@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('auth.login'))

# ----------------- Client signup -----------------
@bp.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    form = SignupForm()
    if request.method == 'POST' and form.validate_on_submit():
        userid = form.userid.data.strip()
        password = form.password.data
        email = form.email.data.strip().lower()
        tel_field = getattr(form, 'phone', None) or getattr(form, 'tel_number', None)
        tel_number = tel_field.data.strip().replace('-', '') if tel_field else ''
        name = (getattr(form, 'name', None).data.strip()
                if getattr(form, 'name', None) else
                (getattr(form, 'username', None).data.strip() if getattr(form, 'username', None) else userid))
        y, m, d = form.birth_year.data, form.birth_month.data, form.birth_day.data
        birthday = datetime(y, m, d)

        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if tel_number and User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger'); return redirect(url_for('auth.client_signup'))

        user = User(
            userid=userid,
            password_hash=generate_password_hash(password),
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name if hasattr(User, 'name') else None,
            is_expert=False
        )
        try:
            db.session.add(user); db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('동일한 아이디/이메일/전화번호가 이미 존재합니다.', 'danger')
            return redirect(url_for('auth.client_signup'))

        flash('회원가입이 완료되었습니다.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/client_signup.html', form=form)

# ----------------- Expert signup -----------------
@bp.route('/expert_signup', methods=['GET', 'POST'])
def expert_signup():
    form = ExpertSignupForm()
    if request.method == 'POST' and form.validate_on_submit():
        if not PASSWORD_RE.fullmatch(form.password.data or ''):
            flash('비밀번호는 영문, 숫자, 특수문자 포함 8~20자여야 합니다.', 'danger')
            return render_template('auth/expert_signup.html', form=form)
        if hasattr(form, 'password_confirm') and (form.password.data != form.password_confirm.data):
            flash('비밀번호가 일치하지 않습니다.', 'danger')
            return render_template('auth/expert_signup.html', form=form)

        userid = form.userid.data.strip()
        password = form.password.data
        email = form.email.data.strip().lower()
        tel_number = form.tel_number.data.strip().replace('-', '')
        name = form.name.data.strip()
        y, m, d = form.birth_year.data, form.birth_month.data, form.birth_day.data
        birthday = datetime(y, m, d)
        service = form.service.data
        location = form.location.data

        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger'); return redirect(url_for('auth.expert_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger'); return redirect(url_for('auth.expert_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger'); return redirect(url_for('auth.expert_signup'))

        user = User(
            userid=userid,
            password_hash=generate_password_hash(password),
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name if hasattr(User, 'name') else None,
            is_expert=True,
            service=service if hasattr(User, 'service') else None,
            location=location if hasattr(User, 'location') else None,
        )
        try:
            db.session.add(user); db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('동일한 아이디/이메일/전화번호가 이미 존재합니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))

        flash('전문가 회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/expert_signup.html', form=form)

# ----------------- My page -----------------
@bp.get('/mypage')
@login_required
def mypage():
    user = User.query.get_or_404(session.get('user_id'))
    form = ChangePasswordForm()
    # 템플릿 호환을 위해 current_user 별칭 제공
    return render_template('auth/mypage.html', user=user, current_user=user, form=form)

# ----------------- Edit profile -----------------
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get_or_404(session.get('user_id'))
    form = EditProfileForm(obj=user)
    if request.method == 'POST' and form.validate_on_submit():
        if hasattr(form, 'name'):       user.name = form.name.data.strip()
        if hasattr(form, 'email'):      user.email = form.email.data.strip().lower()
        if hasattr(form, 'tel_number'): user.tel_number = form.tel_number.data.strip().replace('-', '')
        if getattr(user, 'is_expert', False):
            if hasattr(form, 'service'):  user.service  = form.service.data.strip()
            if hasattr(form, 'location'): user.location = form.location.data.strip()
        db.session.commit()
        flash('프로필이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('auth.mypage'))
    return render_template('auth/edit_profile.html', form=form, user=user, current_user=user)

# ----------------- Find ID -----------------
@bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    form = FindIdForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip().lower()
        user = User.query.filter_by(name=name, email=email).first()
        if user:
            return jsonify({'success': True, 'userid': user.userid})
        return jsonify({'success': False, 'message': '일치하는 정보가 없습니다.'})
    return render_template('auth/find_id.html', form=form)

# ----------------- Find / Reset password -----------------
@bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    form = FindPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('해당 이메일로 등록된 사용자가 없습니다.', 'danger')
            return render_template('auth/find_password.html', form=form)

        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        reset_url = url_for('auth.reset_password', token=token, _external=True)
        msg = Message('비밀번호 재설정', recipients=[email])
        msg.body = f"아래 링크를 클릭하여 새 비밀번호를 설정하세요:\n{reset_url}"
        try:
            mail.send(msg)
            flash('비밀번호 재설정 링크가 이메일로 발송되었습니다.', 'success')
        except Exception as e:
            flash(f'이메일 발송 중 오류 발생: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/find_password.html', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
    except Exception:
        flash('유효하지 않거나 만료된 링크입니다.', 'danger')
        return redirect(url_for('auth.find_password'))

    if request.method == 'POST':
        new_password = request.form.get('password') or ''
        if not PASSWORD_RE.fullmatch(new_password):
            flash('비밀번호는 영문, 숫자, 특수문자를 포함한 8~20자여야 합니다.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('비밀번호가 변경되었습니다. 로그인해 주세요.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)

# ----------------- Change password (logged-in) -----------------
@bp.post('/change_password')
@login_required
def change_password():
    user = User.query.get_or_404(session.get('user_id'))
    form = ChangePasswordForm()

    if not form.validate_on_submit():
        for _, errs in form.errors.items():
            for e in errs:
                flash(e, 'danger')
        return redirect(url_for('auth.mypage'))

    if not check_password_hash(user.password_hash, form.current_password.data or ''):
        flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('auth.mypage'))

    new_password = form.new_password.data
    if not PASSWORD_RE.fullmatch(new_password):
        flash('비밀번호는 영문, 숫자, 특수문자를 포함한 8~20자여야 합니다.', 'danger')
        return redirect(url_for('auth.mypage'))

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
    return redirect(url_for('auth.mypage'))
