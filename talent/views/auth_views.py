from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_mail import Message
import jwt
import os

from talent import db, mail
from talent.models import User

# Blueprint setup
bp = Blueprint('auth', __name__, url_prefix='/auth')

# ----------------- Login -----------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        user = User.query.filter_by(userid=userid).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash(f'{user.userid}님, 로그인되었습니다!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다.', 'danger')
    return render_template('auth/login.html')

# ----------------- Client Signup -----------------
@bp.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        email = request.form.get('email')
        tel_number = request.form.get('tel_number')
        name = request.form.get('name')

        # 중복 체크
        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))

        # 비밀번호 해싱
        hashed_password = generate_password_hash(password)

        # 생년월일 처리
        try:
            birthday = datetime(
                int(request.form.get("birth_year")),
                int(request.form.get("birth_month")),
                int(request.form.get("birth_day"))
            )
        except (TypeError, ValueError):
            flash("생년월일이 유효하지 않습니다.", "danger")
            return redirect(url_for("auth.client_signup"))

        new_user = User(
            userid=userid,
            password_hash=hashed_password,
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name,
            is_expert=False
        )

        db.session.add(new_user)
        db.session.commit()
        flash("일반 회원가입이 완료되었습니다! 로그인해 주세요.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/client_signup.html')

# ----------------- Expert Signup -----------------
@bp.route('/expert_signup', methods=['GET', 'POST'])
def expert_signup():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        email = request.form.get('email')
        tel_number = request.form.get('tel_number')
        name = request.form.get('name')
        service = request.form.get('service')
        location = request.form.get('location')

        # 중복 체크
        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))

        hashed_password = generate_password_hash(password)

        try:
            birthday = datetime(
                int(request.form.get("birth_year")),
                int(request.form.get("birth_month")),
                int(request.form.get("birth_day"))
            )
        except (TypeError, ValueError):
            flash("생년월일이 유효하지 않습니다.", "danger")
            return redirect(url_for("auth.expert_signup"))

        new_user = User(
            userid=userid,
            password_hash=hashed_password,
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name,
            is_expert=True,
            service=service,
            location=location
        )

        db.session.add(new_user)
        db.session.commit()
        flash("전문가 회원가입이 완료되었습니다! 로그인해 주세요.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/expert_signup.html')

# ----------------- Find ID -----------------
@bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        user = User.query.filter_by(name=name, email=email).first()
        if user:
            return jsonify({'success': True, 'userid': user.userid})
        return jsonify({'success': False, 'message': '일치하는 정보가 없습니다.'})
    return render_template('auth/find_id.html')

# ----------------- Find Password -----------------
@bp.route('/find_password', methods=['GET', 'POST'])
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
            msg.body = f'''안녕하세요, {user.name}님!\n\n비밀번호 재설정을 요청하셨습니다. 아래 링크를 클릭하여 새 비밀번호를 설정해주세요:\n\n{reset_url}\n\n이 링크는 1시간 동안 유효합니다.'''
            try:
                mail.send(msg)
                flash('비밀번호 재설정 링크가 이메일로 발송되었습니다.', 'success')
            except Exception as e:
                flash(f'이메일 발송 중 오류가 발생했습니다: {str(e)}', 'danger')
            return redirect(url_for('auth.login'))
        else:
            flash('해당 이메일로 등록된 사용자가 없습니다.', 'danger')
    return render_template('auth/find_password.html')

# ----------------- Reset Password -----------------
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # 실제 토큰 검증과 비밀번호 재설정 로직 구현 필요
    flash("비밀번호 재설정 페이지 (임시)", "info")
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
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.tel_number = request.form.get('tel_number')
        if user.is_expert:
            user.service = request.form.get('service')
            user.location = request.form.get('location')
        db.session.commit()
        flash('프로필이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('auth.mypage'))
    return render_template('auth/edit_profile.html', user=user)

# ----------------- Change Password -----------------
@bp.route('/change_password', methods=['POST'])
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
