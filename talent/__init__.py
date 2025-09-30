from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

from . import models

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # config.py 불러오기
    app.config.from_object('talent.config')

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from .views import main_views, auth_views, community_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.auth_bp)
    app.register_blueprint(community_views.community_bp)

    return app
