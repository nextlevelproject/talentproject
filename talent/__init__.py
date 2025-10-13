from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf import CSRFProtect
# from . import models

import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            from .models import User
            g.user = User.query.get(user_id)

    # 확장 등록
    # 1) 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    # 블루프린트 등록
    from .views import main_views, auth_views, store_views, community_views
    # 2) init 이후에만 내부 모듈 임포트 (순환 방지)
    from . import models

    # 3) 블루프린트 등록
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(store_views.bp)
    app.register_blueprint(community_views.bp)

    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app
