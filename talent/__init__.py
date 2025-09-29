from flask import Flask, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

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
    mail.init_app(app)

    # 블루프린트 정의 (예: auth)
    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

    @auth_bp.route('/client_signup')
    def client_signup():
        return render_template('auth/client_signup.html')

    @auth_bp.route('/login')
    def login():
        return render_template('auth/login.html')

    # 더 필요한 라우트들 auth_bp에 추가 가능

    # 블루프린트 등록
    app.register_blueprint(auth_bp)

    # 메인 페이지 블루프린트도 비슷하게 등록 가능
    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    def index():
        return render_template('index.html')

    app.register_blueprint(main_bp)

    return app

# 직접 실행 시
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)