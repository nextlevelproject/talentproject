from talent import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    tel_number = db.Column(db.String(120), unique=True, nullable=False)

   # expert_signup.html 에서 추가된 필드들 (고수에게만 해당)
    name = db.Column(db.String(100), nullable=True) # 실명
    service = db.Column(db.String(200), nullable=True) # 제공 서비스 (쉼표로 구분할 수도 있음)
    location = db.Column(db.String(100), nullable=True) # 지역


    is_expert = db.Column(db.Boolean, default=False)

    # 소셜 로그인 관련 필드
    social_id = db.Column(db.String(200), nullable=True)  # 소셜 계정 ID
    social_type = db.Column(db.String(20), nullable=True)  # 'kakao', 'naver', 'google' 등