from flask import Flask, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

import config
from . import models  # ensure models are loaded

# 확장 객체 전역 선언 (앱과 나중에 연결)

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # 앱 설정 (config.py 대신 간단히 직접 설정)
    app.config['SECRET_KEY'] = 'c85a9e21d0f5477f9f32f227ea72d7e0e3baf65a42f7c53be9a61a3cfa77d234'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///talent.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 익스텐션(app과 연결)
    db.init_app(app)
    migrate.init_app(app, db)

    # 블루 프린트 등록
    from .views import main_views, auth_views, community_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(community_views.bp)
    app.register_blueprint(auth_bp)
    return app

    mail.init_app(app)
    return app

# 직접 실행 시
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
