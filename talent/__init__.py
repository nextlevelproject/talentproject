# talent/__init__.py
from flask import Flask
from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

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

    from . import models

    # 블루프린트 등록
    from .views import main_views, auth_views, store_views, community_views, category_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(store_views.bp)
    app.register_blueprint(community_views.bp)
    app.register_blueprint(category_views.bp)

    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app
