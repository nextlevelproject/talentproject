# talent/__init__.py
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager, current_user
import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()  # 👈 new

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    import os
    upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'community_uploads')
    os.makedirs(upload_folder, exist_ok=True)  # ensure folder exists
    app.config['UPLOAD_FOLDER'] = upload_folder

    # --- Flask-Login setup ---
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # import inside function to avoid circular import
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- backward compatibility for team code using g.user ---
    @app.before_request
    def load_user_to_g():
        g.user = current_user if current_user.is_authenticated else None

    # --- extension init ---
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # --- blueprints ---
    from .views import main_views, auth_views, store_views, community_views, category_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(store_views.bp)
    app.register_blueprint(community_views.bp)
    app.register_blueprint(category_views.bp)

    # --- custom filters ---
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app
