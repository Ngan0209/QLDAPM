from flask import Flask
from urllib.parse import quote
import os
from dotenv import load_dotenv
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.google import make_google_blueprint

from app.models import User, Templates
from app.extensions import db, login, migrate   # lấy từ extensions
from app.routes.home import home_bp
from app.routes.auth import auth_bp
from app.routes.job_application import cv_bp
from app.models import User
from app.admin.admin import init_admin

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'my_default_secret_key')
    db_url = os.getenv("DATABASE_URL")
    db_password = os.getenv("DATABASE_PASSWORD")

    if db_password:
        db_url = db_url % quote(db_password)

    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/job_db?charset=utf8mb4" % quote('Abc123')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    init_admin(app)

    # cấu hình login
    login.login_view = "auth.login"

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

        # Google OAuth
    google_bp = make_google_blueprint(
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scope=["profile", "email"],
            redirect_to="google_login"
        )
    app.register_blueprint(google_bp, url_prefix="/login")

        # Facebook OAuth
    facebook_bp = make_facebook_blueprint(
            client_id=os.getenv("FACEBOOK_APP_ID"),
            client_secret=os.getenv("FACEBOOK_APP_SECRET"),
            redirect_to="facebook_login"
        )

    # đăng ký blueprint
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cv_bp, url_prefix="/cv")


    return app
