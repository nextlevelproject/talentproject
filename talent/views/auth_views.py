# talent/views/auth_views.py
# 필요한 Flask 모듈들을 임포트
from flask import Flask,Blueprint, request, flash, redirect, url_for, render_template, jsonify, session, current_app
# 비밀번호 해싱을 위한 모듈 임포트
from werkzeug.security import generate_password_hash, check_password_hash
# 생년월일 처리를 위한 모듈 임포트
from datetime import datetime
# 정의한 User 모델 임포트
from talent.models import User
from werkzeug.security import generate_password_hash

from talent import db, mail
# 기존 임포트 문 아래에 추가
import jwt  # pip install pyjwt 필요
from datetime import timedelta  # datetime은 이미 임포트되어 있음
from flask_mail import Message  # 메일 발송용



# 데이터베이스 객체 임포트 (db 객체가 어디서 생성되는지에 따라 경로가 달라질 수 있음)
# 일반적으로 'from talent import db' 라고 한다면, talent/__init__.py 에 db 객체가 생성되었을 가능성이 큼


# Blueprint 객체 생성
# 'auth'는 이 블루프린트의 이름이고, url_prefix='/auth'는 이 블루프린트의 모든 라우트에 '/auth'가 앞에 붙는다는 의미
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f) # 이 데코레이터는 함수의 메타데이터를 유지해줘
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요한 기능입니다.', 'danger') # 메시지는 여기에!
            return redirect(url_for('auth.login')) # 로그인 페이지로 리다이렉트!
        return f(*args, **kwargs) # 로그인되어 있으면 원래 함수 실행
    return decorated_function



# 참고: 이 파일에는 'app = Flask(__name__)' 같은 코드가 들어가면 안 됨.
# Flask 앱 객체는 프로젝트의 최상위 app.py (또는 __init__.py) 같은 곳에서 단 한 번만 생성해야 함.

# --- 로그인 라우트 ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 폼에서 입력받은 아이디(또는 이메일)와 비밀번호를 가져옴
        userid = request.form.get('userid')  # 폼에서 'name="userid"' 로 넘어왔다고 가정
        password = request.form.get('password')

        # 데이터베이스에서 해당 userid를 가진 사용자를 찾음
        user = User.query.filter_by(userid=userid).first()

        # 사용자가 존재하고 비밀번호가 일치하는지 확인
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  # 세션에 사용자 ID 저장 (로그인 상태 유지)
            flash(f'{user.userid}님, 로그인되었습니다!', 'success')  # 로그인 성공 메시지
            # 'main.index'는 'main' 블루프린트에 있는 'index' 함수를 가리킴 (메인 페이지로 이동)
            return redirect(url_for('main.index'))
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다.', 'danger')  # 로그인 실패 메시지
    return render_template('auth/login.html')  # GET 요청 시 로그인 폼 렌더링
  
@bp.route("/signup", methods=["POST"])
def signup():
    year = request.form.get("birth_year")
    month = request.form.get("birth_month")
    day = request.form.get("birth_day")

# --- 일반 사용자 회원가입 라우트 ---
@bp.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        email = request.form.get('email')
        tel_number = request.form.get('tel_number')
        name = request.form.get('name')  # 'client_signup.html' 폼에 'name' 필드가 있어야 함

        # 사용자 중복체크 (아이디, 이메일, 전화번호 중복 여부 확인)
        if User.query.filter_by(userid=userid).first():
            flash('이미 존재하는 아이디입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))
        if User.query.filter_by(tel_number=tel_number).first():
            flash('이미 사용 중인 전화번호입니다.', 'danger')
            return redirect(url_for('auth.client_signup'))

        # 비밀번호 해쉬화 (보안을 위해 평문 비밀번호를 DB에 저장하지 않음)
        hashed_password = generate_password_hash(password)

        # 생년월일 처리
        year = request.form.get("birth_year")
        month = request.form.get("birth_month")
        day = request.form.get("birth_day")

        try:
            birthday = datetime(int(year), int(month), int(day))
        except (TypeError, ValueError):
            flash("생년월일이 유효하지 않습니다.", "danger")
            return redirect(url_for("auth.client_signup"))

        # 새로운 User 객체 생성
        # 'role' 필드는 User 모델에 있다면 여기에 'client'로 저장하면 좋음
        new_user = User(
            userid=userid,
            password_hash=hashed_password,
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name,
            is_expert=False,  # 일반 사용자이므로 is_expert는 False
            # role='client' # User 모델에 role 필드가 있다면 추가
        )

        # 데이터베이스에 사용자 정보 추가 및 저장
        db.session.add(new_user)
        db.session.commit()
        flash("일반 회원가입이 완료되었습니다! 로그인해 주세요.", "success")
        return redirect(url_for('auth.login'))  # 회원가입 성공 후 로그인 페이지로 이동
    return render_template('auth/client_signup.html')  # GET 요청 시 일반 사용자 회원가입 폼 렌더링


# --- 전문가 회원가입 라우트 ---
@bp.route('/expert_signup', methods=['GET', 'POST'])
def expert_signup():
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')
        email = request.form.get('email')
        tel_number = request.form.get('tel_number')
        name = request.form.get('name')
        service = request.form.get('service')  # expert_signup.html 폼에 'service' 필드가 있어야 함
        location = request.form.get('location')  # expert_signup.html 폼에 'location' 필드가 있어야 함

        # 사용자 중복체크
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

        # 생년월일 처리
        year = request.form.get("birth_year")
        month = request.form.get("birth_month")
        day = request.form.get("birth_day")

        try:
            birthday = datetime(int(year), int(month), int(day))
        except (TypeError, ValueError):
            flash("생년월일이 유효하지 않습니다.", "danger")
            return redirect(url_for("auth.expert_signup"))

        # 새로운 User 객체 생성 (전문가 전용 필드 포함)
        new_user = User(
            userid=userid,
            password_hash=hashed_password,
            email=email,
            birthday=birthday,
            tel_number=tel_number,
            name=name,
            is_expert=True,  # 전문가이므로 is_expert는 True
            service=service,  # User 모델에 'service' 필드가 있어야 함
            location=location,  # User 모델에 'location' 필드가 있어야 함
            # role='expert' # User 모델에 role 필드가 있다면 추가
        )

        db.session.add(new_user)
        db.session.commit()
        flash("전문가 회원가입이 완료되었습니다! 로그인해 주세요.", "success")
        return redirect(url_for('auth.login'))  # 회원가입 성공 후 로그인 페이지로 이동
    return render_template('auth/expert_signup.html')  # GET 요청 시 전문가 회원가입 폼 렌더링


# --- 아이디 찾기 라우트 ---
@bp.route('/find_id', methods=['GET', 'POST'])
def find_id():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        # User 모델에 'name' 컬럼이 있어야 정상 작동하며, 'email' 필드도 User 모델에 있어야 함
        user = User.query.filter_by(name=name, email=email).first()

        if user:
            return jsonify({'success': True, 'userid': user.userid})
        else:
            return jsonify({'success': False, 'message': '일치하는 정보가 없습니다.'})

    return render_template('auth/find_id.html')  # GET 요청 시 아이디 찾기 폼 렌더링



# --- 비밀번호 찾기 라우트 ---
@bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # 토큰 생성 (1시간 유효)
            token = jwt.encode(
                {
                    'user_id': user.id,
                    'exp': datetime.utcnow() + timedelta(hours=1)
                },
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )

            # 비밀번호 재설정 링크 생성
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            # 이메일 발송
            msg = Message('비밀번호 재설정', recipients=[email])
            msg.body = f'''안녕하세요, {user.name}님!

비밀번호 재설정을 요청하셨습니다. 아래 링크를 클릭하여 새 비밀번호를 설정해주세요:

{reset_url}

이 링크는 1시간 동안 유효합니다.
본인이 요청하지 않았다면 이 이메일을 무시하시면 됩니다.

감사합니다.
매칭허브 팀
'''
            try:
                mail.send(msg)
                flash('비밀번호 재설정 링크가 이메일로 발송되었습니다.', 'success')
            except Exception as e:
                flash(f'이메일 발송 중 오류가 발생했습니다: {str(e)}', 'danger')
            return redirect(url_for('auth.login'))
        else:
            flash('해당 이메일로 등록된 사용자가 없습니다.', 'danger')
    return render_template('auth/find_password.html')

# --- 비밀번호 재설정 라우트 ---
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        birthday = datetime(int(year), int(month), int(day))
    except (TypeError, ValueError):
        flash("생년월일이 유효하지 않습니다.", "danger")
        return redirect(url_for("signup"))

    password = request.form.get("password")
    if not password:
        flash("비밀번호를 입력해주세요.", "danger")
        return redirect(url_for("signup"))
    hashed_password = generate_password_hash(password)

    new_user = User(
        userid=request.form["id"],
        password=hashed_password,
        email=request.form["email"] + "@naver.com",  # 도메인 처리 필요
        birthday=birthday,
        tel_number=request.form["tel_number"]
    )

    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("/auth/login.html"))
  
    # --- 마이페이지 라우트 ---
    @bp.route('/mypage')
    @login_required  # 로그인한 사용자만 접근 가능
    def mypage():
        # 세션에서 현재 로그인한 사용자의 ID를 가져와서 해당 사용자 정보를 조회
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)  # 사용자가 없으면 404 오류

        # 사용자 정보를 mypage.html 템플릿으로 전달
        return render_template('auth/mypage.html', user=user)

    # --- 프로필 수정 라우트 ---
    @bp.route('/edit_profile', methods=['GET', 'POST'])
    @login_required  # 로그인한 사용자만 접근 가능
    def edit_profile():
        # 세션에서 현재 로그인한 사용자의 ID를 가져와서 해당 사용자 정보를 조회
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)

        if request.method == 'POST':
            # POST 요청일 때 (폼 제출 시) 사용자 정보 업데이트
            user.name = request.form.get('name')
            user.email = request.form.get('email')
            user.tel_number = request.form.get('tel_number')

            # 전문가인 경우 추가 정보 업데이트
            if user.is_expert:
                user.service = request.form.get('service')
                user.location = request.form.get('location')

            # 변경사항 저장
            db.session.commit()
            flash('프로필이 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('auth.mypage'))

        # GET 요청일 때 (페이지 접속 시) 프로필 수정 폼 표시
        return render_template('auth/edit_profile.html', user=user)

    # --- 비밀번호 변경 라우트 ---
    @bp.route('/change_password', methods=['POST'])
    @login_required  # 로그인한 사용자만 접근 가능
    def change_password():
        # 세션에서 현재 로그인한 사용자의 ID를 가져와서 해당 사용자 정보를 조회
        user_id = session.get('user_id')
        user = User.query.get_or_404(user_id)

        # 폼에서 입력한 현재 비밀번호와 새 비밀번호 가져오기
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # 현재 비밀번호가 맞는지 확인
        if not check_password_hash(user.password_hash, current_password):
            flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('auth.mypage'))

        # 새 비밀번호와 확인 비밀번호가 일치하는지 확인
        if new_password != confirm_password:
            flash('새 비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('auth.mypage'))

        # 새 비밀번호로 업데이트
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
        return redirect(url_for('auth.mypage'))