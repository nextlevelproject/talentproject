from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM 적용
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models  # ensure models are loaded

    # 블루프린트 등록
    from .views import main_views, community_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(community_views.bp)

    return app
