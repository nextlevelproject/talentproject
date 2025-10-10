# talent/views/auth_views.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
import jwt, re

from talent import db, mail
from talent.models import User
from talent.forms import (
    LoginForm,
    SignupForm,
    ExpertSignupForm,
    EditProfileForm,
    FindIdForm,
    FindPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
)

# ------------------ 공통: 로그인 필요 데코레이터 ------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요한 기능입니다.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# Blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

# ----------------- Login -----------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        userid = form.userid.data.strip()
        password = form.password.data
        user = User.query.filter_by(userid=userid).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
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

# ----------------- Client Signup -----------------
@bp.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    form = SignupForm()
    if form.validate_on_submit():
        userid = form.userid.data.strip()
        password = form.password.data
        email = form.email.data.strip().lower()
        tel_number = form.phone.data.strip().replace('-', '')
        name = form.name.data.strip()
        y, m, d = form.birth_year.data, form.birth_month.data, form.birth_day.data
        birthday = datetime(y, m, d)

        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger'); return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger'); return redirect(url_for('auth.client_signup'))

        user = User(userid=userid,
                    password_hash=generate_password_hash(password),
                    email=email, birthday=birthday, tel_number=tel_number,
                    name=name, is_expert=False)
        try:
            db.session.add(user); db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('동일한 아이디/이메일/전화번호가 이미 존재합니다.', 'danger')
            return redirect(url_for('auth.client_signup'))

        flash('회원가입이 완료되었습니다.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/client_signup.html', form=form)

# ----------------- Expert Signup -----------------
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

        # 저장
        user = User(
            userid=userid,
            password_hash=generate_password_hash(password),
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name,
            is_expert=True,
            service=service,
            location=location,
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('동일한 아이디/이메일/전화번호가 이미 존재합니다.', 'danger')
            return redirect(url_for('auth.expert_signup'))

        flash('전문가 회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
        return redirect(url_for('auth.login'))

    # GET 또는 검증 실패 시
    return render_template('auth/expert_signup.html', form=form)

