from flask import Flask
from urllib.parse import quote
import os
from dotenv import load_dotenv

from .extensions import db, login, migrate   # lấy từ extensions
from .routes.home import home_bp
from .routes.auth import auth_bp
from .models import User

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

    # cấu hình login
    login.login_view = "auth.login"

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # đăng ký blueprint
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
