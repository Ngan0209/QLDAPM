from flask import Flask
from urllib.parse import quote
import os
from dotenv import load_dotenv
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .models import User, Templates
from .extensions import db, login, migrate   # lấy từ extensions
from .routes.company import company_bp
from .routes.home import home_bp
from .routes.auth import auth_bp
from .routes.job_application import cv_bp
from .models import User
from .admin.admin import init_admin
from .routes.job_posting import job_posting_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    db_url = os.getenv("DATABASE_URL")
    db_password = os.getenv("DATABASE_PASSWORD")

    if db_password:
        db_url = db_url % quote(db_password)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
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

    # đăng ký blueprint
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cv_bp, url_prefix="/cv")
    app.register_blueprint(job_posting_bp, url_prefix="/job")
    app.register_blueprint(company_bp, url_prefix="/company")

    return app
