# talent/views/auth_views.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
import jwt, re

from talent.models import User
from talent import db, mail

# ---------- 공용 정규식 ----------
PASSWORD_RE = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,20}$')
USERID_RE   = re.compile(r'^[a-zA-Z0-9_]{6,20}$')
EMAIL_RE    = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
PHONE_RE    = re.compile(r'^\d{9,11}$')

# ------------------ 공통: 로그인 필요 데코레이터 ------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요한 기능입니다.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# Blueprint setup
bp = Blueprint('auth', __name__, url_prefix='/auth')

# ----------------- Login -----------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = (request.form.get('userid') or '').strip()
        password = request.form.get('password') or ''
        user = User.query.filter_by(userid=userid).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            flash(f'{user.userid}님, 로그인되었습니다.', 'success')
            return redirect(url_for('main.index'))
        flash('아이디 또는 비밀번호가 틀렸습니다.', 'danger')
    return render_template('auth/login.html')

# ----------------- Logout -----------------
@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('auth.login'))

# ----------------- Client Signup -----------------
@bp.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    if request.method == 'POST':
        userid = (request.form.get('userid') or '').strip()
        password = request.form.get('password') or ''
        password_confirm = request.form.get('password_confirm') or ''
        email = (request.form.get('email') or '').strip().lower()
        tel_number = (request.form.get('tel_number') or '').strip().replace('-', '')
        name = (request.form.get('name') or '').strip()

        # 1) 형식/길이/공백 검증
        if not USERID_RE.fullmatch(userid):
            flash('아이디는 영문/숫자/밑줄 6~20자여야 합니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if not PASSWORD_RE.fullmatch(password):
            flash('비밀번호는 영문, 숫자, 특수문자를 포함한 8~20자여야 합니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if not EMAIL_RE.fullmatch(email):
            flash('이메일 형식이 올바르지 않습니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if not PHONE_RE.fullmatch(tel_number):
            flash('전화번호는 숫자 9~11자리여야 합니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if not name:
            flash('이름은 필수입니다.', 'danger'); return redirect(url_for('auth.client_signup'))

        # 2) 생년월일 파싱
        try:
            y = int(request.form['birth_year']); m = int(request.form['birth_month']); d = int(request.form['birth_day'])
            birthday = datetime(y, m, d)
        except Exception:
            flash('생년월일이 유효하지 않습니다.', 'danger'); return redirect(url_for('auth.client_signup'))

        # 3) 중복 체크
        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger'); return redirect(url_for('auth.client_signup'))

        # 4) 생성 및 저장
        user = User(userid=userid, password_hash=generate_password_hash(password),
                    email=email, birthday=birthday, tel_number=tel_number, name=name, is_expert=False)
        try:
            db.session.add(user); db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('동일한 아이디/이메일/전화번호가 이미 존재합니다.', 'danger')
            return redirect(url_for('auth.client_signup'))

        flash('회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/client_signup.html')

# ----------------- Expert Signup -----------------
@bp.route('/expert_signup', methods=['GET', 'POST'])
def expert_signup():
    if request.method == 'POST':
        userid = (request.form.get('userid') or '').strip()
        password = request.form.get('password') or ''
        email = (request.form.get('email') or '').strip().lower()
        tel_number = (request.form.get('tel_number') or '').strip().replace('-', '')
        name = (request.form.get('name') or '').strip()
        service = (request.form.get('service') or '').strip()
        location = (request.form.get('location') or '').strip()

        if not USERID_RE.fullmatch(userid):
            flash('아이디는 영문/숫자/밑줄 6~20자여야 합니다.', 'danger'); return redirect(url_for('auth.expert_signup'))
        if not PASSWORD_RE.fullmatch(password):
            flash('비밀번호는 영문, 숫자, 특수문자를 포함한 8~20자여야 합니다.', 'danger'); return redirect(url_for('auth.expert_signup'))
        if not EMAIL_RE.fullmatch(email):
            flash('이메일 형식이 올바르지 않습니다.', 'danger'); return redirect(url_for('auth.expert_signup'))
        if not PHONE_RE.fullmatch(tel_number):
            flash('전화번호는 숫자 9~11자리여야 합니다.', 'danger'); return redirect(url_for('auth.expert_signup'))
        if not all([name, service, location]):
            flash('이름/서비스/지역은 필수입니다.', 'danger'); return redirect(url_for('auth.expert_signup'))

        try:
            y = int(request.form['birth_year']); m = int(request.form['birth_month']); d = int(request.form['birth_day'])
            birthday = datetime(y, m, d)
        except Exception:
            flash('생년월일이 유효하지 않습니다.', 'danger'); return redirect(url_for('auth.expert_signup'))

        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger'); return redirect(url_for('auth.expert_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger'); return redirect(url_for('auth.expert_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger'); return redirect(url_for('auth.expert_signup'))

        user = User(userid=userid, password_hash=generate_password_hash(password), email=email,
                    birthday=birthday, tel_number=tel_number, name=name, is_expert=True,
                    service=service, location=location)
        try:
            db.session.add(user); db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('동일한 아이디/이메일/전화번호가 이미 존재합니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))

        flash('전문가 회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/expert_signup.html')

# ----------------- Find ID -----------------
@bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        user = User.query.filter_by(name=name, email=email).first()
        if user:
            return jsonify({'success': True, 'userid': user.userid})
        return jsonify({'success': False, 'message': '일치하는 정보가 없습니다.'})
    return render_template('auth/find_id.html')

# ----------------- Find Password -----------------
@bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
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
    return render_template('auth/find_password.html')

# ------------------ 비밀번호 재설정 ------------------
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

# ----------------- Mypage -----------------
@bp.route('/mypage')
@login_required
def mypage():
    user = User.query.get_or_404(session.get('user_id'))
    return render_template('auth/mypage.html', user=user)

# ----------------- Edit Profile -----------------
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get_or_404(session.get('user_id'))
    if request.method == 'POST':
        user.name = (request.form.get('name') or '').strip()
        user.email = (request.form.get('email') or '').strip().lower()
        user.tel_number = (request.form.get('tel_number') or '').strip().replace('-', '')
        if user.is_expert:
            user.service = (request.form.get('service') or '').strip()
            user.location = (request.form.get('location') or '').strip()
        db.session.commit()
        flash('프로필이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('auth.mypage'))
    return render_template('auth/edit_profile.html', user=user)

# ----------------- Change Password -----------------
@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get_or_404(session.get('user_id'))
    current_password = request.form.get('current_password') or ''
    new_password = request.form.get('new_password') or ''
    confirm_password = request.form.get('confirm_password') or ''

    if not check_password_hash(user.password_hash, current_password):
        flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('auth.mypage'))
    if new_password != confirm_password:
        flash('새 비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('auth.mypage'))
    if not PASSWORD_RE.fullmatch(new_password):
        flash('새 비밀번호는 영문, 숫자, 특수문자를 포함한 8~20자여야 합니다.', 'danger')
        return redirect(url_for('auth.mypage'))

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
    return redirect(url_for('auth.mypage'))
