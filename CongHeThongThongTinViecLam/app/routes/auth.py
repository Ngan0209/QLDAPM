from flask import Blueprint, request, jsonify, flash
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import User, UserRole
from werkzeug.security import generate_password_hash, check_password_hash
from config import upload_avatar
from flask import redirect, url_for
from flask import Blueprint, render_template
from flask_login import login_required
from flask_dance.contrib.google import google
from flask_dance.contrib.facebook import facebook

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
        return render_template("auth/login.html", error="Thiếu thông tin bắt buộc")

    if password != password_confirm:
        return render_template("auth/login.html", error="Mật khẩu xác nhận không khớp")

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return render_template("auth/login.html", error="Username hoặc Email đã tồn tại")

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
        user_type=UserRole.candidate.value,
        dob=dob,
        avatar=avatar_url
    )

    db.session.add(user)
    db.session.commit()

    # Thành công
    return render_template("auth/login.html", message="Đăng ký thành công, hãy đăng nhập!")



@auth_bp.route("/me", methods=["GET"])
@login_required
def get_user_info():
    user = current_user
    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "phone": user.phone,
        "dob": user.dob.strftime("%Y-%m-%d") if user.dob else None,
        "avatar_url": user.avatar,
        "role": user.user_type.value
    })

@auth_bp.route("/profile", methods=["GET"])
@login_required
def profile_screen():
    user = current_user
    return render_template("auth/profile.html", user=user)


@auth_bp.route("/login-screen",endpoint="login-screen")
def login_screen():
    return render_template("auth/login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form
    username = data.get("username")
    password = data.get("password")
    remember = bool(data.get("remember"))

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return render_template("auth/login.html", error="Sai username hoặc password"), 401

    login_user(user, remember=remember)
    if user.user_type == UserRole.admin.value:
        return redirect(url_for("admin.index"))

    # Redirect sang trang profile
    return redirect(url_for("auth.profile_screen"))


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login-screen'))

# Đăng nhập với Google
@auth_bp.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    user_info = resp.json()
    email = user_info.get("email")
    name = user_info.get("name")

    # Xử lý đăng nhập hoặc tạo tài khoản mới
    flash(f"Đăng nhập thành công với Google: {name} ({email})", "success")
    return redirect(url_for("home"))

# Đăng nhập với Facebook
@auth_bp.route("/facebook")
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me?fields=id,name,email")
    user_info = resp.json()
    email = user_info.get("email")
    name = user_info.get("name")

    flash(f"Đăng nhập thành công với Facebook: {name} ({email})", "success")
    return redirect(url_for("home"))