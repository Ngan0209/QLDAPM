from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import User, UserRole
from werkzeug.security import generate_password_hash, check_password_hash
from config import upload_avatar
from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register-screen",endpoint="register-screen")
def register_screen():
    return render_template("auth/register.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    password_confirm = data.get("password_confirm")
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    phone = data.get("phone")
    dob = data.get("dob")

    # Validate cơ bản
    if not username or not email or not password:
        return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400

    if password != password_confirm:
        return jsonify({"error": "Mật khẩu xác nhận không khớp"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username hoặc Email đã tồn tại"}), 400

    # Hash password
    hashed_pw = generate_password_hash(password)

    # Xử lý avatar nếu có
    avatar_url = None
    if "avatar" in request.files and request.files["avatar"].filename != "":
        avatar_file = request.files["avatar"]
        avatar_url = upload_avatar(avatar_file)

    # Tạo user
    user = User(
        username=username,
        email=email,
        password=hashed_pw,
        firstname=firstname,
        lastname=lastname,
        phone=phone,
        user_type=UserRole.candidate,
        dob=dob,
        avatar=avatar_url
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Đăng ký thành công",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "phone": user.phone,
        "dob": user.dob,
        "avatar_url": avatar_url
    }), 201


@auth_bp.route("/login-screen",endpoint="login-screen")
def login_screen():
    return render_template("auth/login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form
    username = data.get("username")
    password = data.get("password")
    print(f"{username} - {password}")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Sai username hoặc password"}), 401

    login_user(user)
    return jsonify({"message": "Đăng nhập thành công", "user_id": user.id, "role": user.user_type.value})



@auth_bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify({"message": "Đăng xuất thành công"})
    return jsonify({"error": "Chưa đăng nhập"}), 400
