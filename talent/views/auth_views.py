from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify, g
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import jwt, re

from talent import db, mail
from talent.models import User
from talent.forms import SignupForm, ExpertSignupForm, EditProfileForm, FindIdForm, FindPasswordForm, LoginForm, ChangePasswordForm, ResetPasswordForm

PASSWORD_RE = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,20}$')
USERID_RE   = re.compile(r'^[a-zA-Z0-9_]{6,20}$')
EMAIL_RE    = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
PHONE_RE    = re.compile(r'^\d{9,11}$')

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요한 기능입니다.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(userid=form.userid.data).first()
        if not user:
            user = User(
                username=form.username.data,
                userid=form.userid.data,
                password_hash=generate_password_hash(form.password1.data),
                email=form.email.data,
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('이미 존재하는 사용자입니다.')
    return render_template('auth/signup.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        userid = (request.form.get('userid') or '').strip()
        password = request.form.get('password') or ''
        user = User.query.filter_by(userid=userid).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id   # ✅ 세션에 user_id 저장
            session['is_expert'] = bool(user.is_expert)  # ✅ 추가
            flash(f'{user.userid}님, 로그인되었습니다.', 'success')
            return redirect(url_for('main.index'))
        flash('아이디 또는 비밀번호가 틀렸습니다.', 'danger')
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('main.index'))

@bp.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    form = SignupForm()
    if form.validate_on_submit():
        userid = form.userid.data.strip()
        password = form.password.data
        email = form.email.data.strip().lower()
        tel_number = form.phone.data.strip().replace('-', '')
        name = form.name.data.strip()

        # 생년월일 조합
        y, m, d = form.birth_year.data, form.birth_month.data, form.birth_day.data
        birthday = datetime(y, m, d)

        # 3) 중복 체크
        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))

        # 저장
        user = User(
            userid=userid,
            password_hash=generate_password_hash(password),
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name,
            is_expert=False
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('동일한 아이디/이메일/전화번호가 이미 존재합니다.', 'danger')
            return redirect(url_for('auth.client_signup'))

        flash('회원가입이 완료되었습니다.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/client_signup.html', form=form)

@bp.route('/expert_signup', methods=['GET', 'POST'])
def expert_signup():
    form = ExpertSignupForm()
    if form.validate_on_submit():
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

        user = User(userid=userid,
                    password_hash=generate_password_hash(password),
                    email=email, birthday=birthday, tel_number=tel_number,
                    name=name, is_expert=True, service=service, location=location)
        try:
            db.session.add(user); db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('동일한 아이디/이메일/전화번호가 이미 존재합니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))

        flash('전문가 회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/expert_signup.html', form=form)

@bp.route('/mypage')
@login_required
def mypage():
    user = User.query.get_or_404(session.get('user_id'))
    form = ChangePasswordForm()
    return render_template('auth/mypage.html', user=user, form=form)

from talent.forms import EditProfileForm

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get_or_404(session.get('user_id'))
    form = EditProfileForm(obj=user)  # 기존 user 값을 기본값으로 채움
    if form.validate_on_submit():
        user.name = form.name.data.strip()
        user.email = form.email.data.strip().lower()
        user.tel_number = form.tel_number.data.strip().replace('-', '')
        if user.is_expert:
            user.service = form.service.data.strip()
            user.location = form.location.data.strip()
        db.session.commit()
        flash('프로필이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('auth.mypage'))
    return render_template('auth/edit_profile.html', form=form, user=user)

@bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    form = FindIdForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip().lower()
        user = User.query.filter_by(name=name, email=email).first()
        if user:
            return jsonify({'success': True, 'userid': user.userid})
        return jsonify({'success': False, 'message': '일치하는 정보가 없습니다.'})
    return render_template('auth/find_id.html', form=form)

@bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    form = FindPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = jwt.encode(
                {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
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

        flash('해당 이메일로 등록된 사용자가 없습니다.', 'danger')
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

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get_or_404(session.get('user_id'))
    form = ChangePasswordForm()
    if not form.validate_on_submit():
        for field, errs in form.errors.items():
            for e in errs: flash(e, 'danger')
        return redirect(url_for('auth.mypage'))

    if not check_password_hash(user.password_hash, form.current_password.data or ''):
        flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('auth.mypage'))

    new_password = form.new_password.data
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
    return redirect(url_for('auth.mypage'))