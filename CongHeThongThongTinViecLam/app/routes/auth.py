from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import User, UserRole
from werkzeug.security import generate_password_hash, check_password_hash
from config import upload_avatar

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form  # vì có cả file
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Thiếu thông tin"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username hoặc Email đã tồn tại"}), 400

    hashed_pw = generate_password_hash(password)

    avatar_url = None
    if "avatar" in request.files:
        avatar_file = request.files["avatar"]
        avatar_url = upload_avatar(avatar_file)

    user = User(
        username=username,
        email=email,
        password=hashed_pw,
        firstname=data.get("firstname"),
        lastname=data.get("lastname"),
        phone=data.get("phone"),
        user_type=UserRole.candidate,
        dob=data.get("dob"),
        avatar=avatar_url  # cần thêm cột avatar trong model User
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Đăng ký thành công",
        "user_id": user.id,
        "avatar_url": avatar_url
    }), 201
# Đăng nhập
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Sai username hoặc password"}), 401

    login_user(user)
    return jsonify({"message": "Đăng nhập thành công", "user_id": user.id, "role": user.user_type.value})


# Đăng xuất
@auth_bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify({"message": "Đăng xuất thành công"})
    return jsonify({"error": "Chưa đăng nhập"}), 400
