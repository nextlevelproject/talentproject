# talent/views/auth_views.py
from flask import Blueprint, request, flash, redirect, url_for, render_template, jsonify, session, current_app
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
import jwt

from talent.models import User
from talent import db, mail

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ------------------ 공통: 로그인 필요 데코레이터 ------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요한 기능입니다.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ------------------ 로그인 ------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        user = User.query.filter_by(userid=userid).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash(f'{user.userid}님, 로그인되었습니다.', 'success')
            return redirect(url_for('main.index'))
        flash('아이디 또는 비밀번호가 틀렸습니다.', 'danger')
    return render_template('auth/login.html')


# ------------------ 일반 회원가입 ------------------
@auth_bp.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        email = request.form.get('email')
        tel_number = request.form.get('tel_number')
        name = request.form.get('name')

        # 중복체크
        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))

        # 생년월일 처리
        year, month, day = request.form.get("birth_year"), request.form.get("birth_month"), request.form.get("birth_day")
        try:
            birthday = datetime(int(year), int(month), int(day))
        except Exception:
            flash("생년월일이 유효하지 않습니다.", "danger")
            return redirect(url_for("auth.client_signup"))

        # 사용자 생성
        user = User(
            userid=userid,
            password_hash=generate_password_hash(password),
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name,
            is_expert=False
        )
        db.session.add(user)
        db.session.commit()
        flash("회원가입이 완료되었습니다. 로그인해 주세요.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/client_signup.html')


# ------------------ 전문가 회원가입 ------------------
@auth_bp.route('/expert_signup', methods=['GET', 'POST'])
def expert_signup():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        email = request.form.get('email')
        tel_number = request.form.get('tel_number')
        name = request.form.get('name')
        service = request.form.get('service')
        location = request.form.get('location')

        # 중복체크
        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))

        # 생년월일 처리
        year, month, day = request.form.get("birth_year"), request.form.get("birth_month"), request.form.get("birth_day")
        try:
            birthday = datetime(int(year), int(month), int(day))
        except Exception:
            flash("생년월일이 유효하지 않습니다.", "danger")
            return redirect(url_for("auth.expert_signup"))

        # 사용자 생성
        user = User(
            userid=userid,
            password_hash=generate_password_hash(password),
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name,
            is_expert=True,
            service=service,
            location=location
        )
        db.session.add(user)
        db.session.commit()
        flash("전문가 회원가입이 완료되었습니다. 로그인해 주세요.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/expert_signup.html')


# ------------------ 아이디 찾기 ------------------
@auth_bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        user = User.query.filter_by(name=name, email=email).first()
        if user:
            return jsonify({'success': True, 'userid': user.userid})
        return jsonify({'success': False, 'message': '일치하는 정보가 없습니다.'})
    return render_template('auth/find_id.html')


# ------------------ 비밀번호 찾기 ------------------
@auth_bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = jwt.encode(
                {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
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
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
    except Exception:
        flash("유효하지 않거나 만료된 링크입니다.", "danger")
        return redirect(url_for("auth.find_password"))

    if request.method == 'POST':
        new_password = request.form.get("password")
        if not new_password:
            flash("비밀번호를 입력해주세요.", "danger")
            return redirect(url_for("auth.reset_password", token=token))
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("비밀번호가 변경되었습니다. 로그인해 주세요.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)


# ------------------ 마이페이지 ------------------
@auth_bp.route('/mypage')
@login_required
def mypage():
    user = User.query.get_or_404(session.get('user_id'))
    return render_template('auth/mypage.html', user=user)


# ------------------ 프로필 수정 ------------------
@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get_or_404(session.get('user_id'))
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.tel_number = request.form.get('tel_number')
        if user.is_expert:
            user.service = request.form.get('service')
            user.location = request.form.get('location')
        db.session.commit()
        flash('프로필이 수정되었습니다.', 'success')
        return redirect(url_for('auth.mypage'))
    return render_template('auth/edit_profile.html', user=user)


# ------------------ 비밀번호 변경 ------------------
@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get_or_404(session.get('user_id'))
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not check_password_hash(user.password_hash, current_password):
        flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('auth.mypage'))
    if new_password != confirm_password:
        flash('새 비밀번호가 일치하지 않습니다.', 'danger')
        return redirect(url_for('auth.mypage'))

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
    return redirect(url_for('auth.mypage'))

