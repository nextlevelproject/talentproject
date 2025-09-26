from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail  # Mail 임포트 추가

import config

# 전역적으로 사용할 객체 생성 (아직 Flask 앱과 연결되지 않음)
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()  # Mail 객체 생성 추가


def create_app():
    # Flask 앱 객체 생성
    app = Flask(__name__)

    # config.py 파일에서 앱 설정을 불러옵니다.
    app.config.from_object(config)

    # ORM (SQLAlchemy) 초기화: db 객체를 Flask 앱 'app'과 연결합니다.
    db.init_app(app)

    # Flask-Migrate 초기화: migrate 객체를 Flask 앱과 db 객체에 연결합니다.
    migrate.init_app(app, db)

    # Flask-Mail 초기화: mail 객체를 Flask 앱 'app'과 연결하고 메일 설정 적용
    mail.init_app(app)  # 이 라인이 필요해!

    # SQLAlchemy 모델들을 임포트합니다.
    from . import models

    # 블루프린트 임포트 및 등록
    from .views import main_views, auth_views

    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.auth_bp)

    # 생성 및 설정된 Flask 앱 객체를 반환합니다.
    return app