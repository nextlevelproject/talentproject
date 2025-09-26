# app.py (프로젝트의 메인 진입점 파일)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy # SQLAlchemy 임포트
from flask_migrate import Migrate # Flask-Migrate 사용 시 임포트 (DB 마이그레이션 도구)

# talent 패키지에서 db 객체를 임포트합니다.
# 일반적으로 이 db 객체는 talent/__init__.py 에서 'db = SQLAlchemy()' 와 같이 초기화됩니다.
from talent import db
from talent.views.auth_views import auth_bp  # 인증 관련 블루프린트 임포트
from talent.views.main_views import bp as main_bp  # 메인 페이지 블루프린트 임포트 (bp를 main_bp로 별칭 지정)


# Flask 앱 객체 생성
app = Flask(__name__)


# --- 앱 설정 ---
# 1. 세션 사용을 위한 비밀키 설정 (필수!)
#    * 보안을 위해 실제 배포 시에는 'YOUR_HIGHLY_SECRET_KEY_HERE_AND_MAKE_IT_STRONG_AND_RANDOM' 대신
#      복잡하고 추측 불가능한 무작위 문자열로 반드시 변경해야 합니다.
#    * 이 키는 세션 데이터 암호화, 플래시 메시지 서명 등에 사용됩니다.
app.config['SECRET_KEY'] = 'YOUR_HIGHLY_SECRET_KEY_HERE_AND_MAKE_IT_STRONG_AND_RANDOM'


# 2. 데이터베이스 설정 (SQLAlchemy 사용 시)
#    * 'sqlite:///talent.db'는 프로젝트 루트 폴더에 'talent.db'라는 SQLite 데이터베이스 파일을 사용한다는 의미입니다.
#    * 네 DB 환경(MySQL, PostgreSQL 등)에 맞게 연결 문자열을 수정해야 합니다.
#      예: 'mysql+pymysql://user:password@host/dbname'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///talent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # SQLAlchemy 이벤트 추적을 비활성화 (리소스 절약 및 권장 설정)


# 3. Flask-Migrate 초기화 (데이터베이스 스키마 변경을 관리하기 위해 필요)
#    * db 객체가 먼저 app에 초기화된 후에 migrate 객체를 초기화합니다.
migrate = Migrate(app, db)


# --- DB 객체 초기화 ---
# db 객체를 Flask 애플리케이션 'app'과 연결합니다.
# 이 단계에서 SQLAlchemy가 'app.config'에 있는 DB 설정을 읽어옵니다.
# 'talent/__init__.py'에서 'db = SQLAlchemy()'로만 선언하고 'db.init_app(app)'을 나중에 하는 경우에 이렇게 사용합니다.
with app.app_context(): # 앱 컨텍스트 내에서 db 초기화를 확실히 합니다.
    db.init_app(app) # SQLAlchemy DB 인스턴스를 Flask 앱에 등록합니다.


# --- 블루프린트 등록 ---
# 각 블루프린트의 라우트들이 메인 Flask 앱에 등록되어 URL 요청을 처리할 수 있게 됩니다.
app.register_blueprint(auth_bp)  # /auth/* 경로를 처리하는 인증 관련 라우트 등록
app.register_blueprint(main_bp)  # / 경로를 처리하는 메인 페이지 라우트 등록


# --- 앱 실행 (개발 환경에서 사용) ---
if __name__ == '__main__':
    # 'debug=True'는 개발 시 코드를 변경하면 자동으로 서버가 재시작되고 디버깅 정보를 보여주므로 유용합니다.
    # 하지만 실제 서비스(배포) 시에는 'debug=False'로 설정하여 보안과 성능을 확보해야 합니다.
    app.run(debug=True)