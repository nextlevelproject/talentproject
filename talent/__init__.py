from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config)

    # 익스텐션 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # 블루프린트 등록
    from .views import main_views, community_views, auth_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(community_views.bp)
    app.register_blueprint(auth_views.bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
