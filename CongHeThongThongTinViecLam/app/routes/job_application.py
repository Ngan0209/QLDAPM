from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user,login_required
from ..models import JobApplication
from app.extensions import db
from config import upload_avatar

cv_bp = Blueprint("cv", __name__, url_prefix="/cv")

@cv_bp.route("/create-form", methods=["GET"])
def create_form():
    return render_template("candidate/CV.html")  # file này nằm trong /templates

@cv_bp.route("/create-cv", methods=["POST"])
@login_required
def create_cv():
    user = current_user

    # Nếu gửi FormData, JSON có thể nằm trong một field, ví dụ: 'cv_data'
    cv_data_str = request.form.get("cv_data")
    if not cv_data_str:
        return jsonify({"error": "Missing cv_data"}), 400

    # Nếu cv_data là JSON string, convert về dict
    import json
    try:
        cv_data = json.loads(cv_data_str)
    except json.JSONDecodeError:
        return jsonify({"error": "cv_data is not valid JSON"}), 400

    avatar_url = None
    avatar_file = request.files.get("avatar")
    if avatar_file and avatar_file.filename != "":
        avatar_url = upload_avatar(avatar_file)

    # Tạo JobApplication mới
    app = JobApplication(
        user_id=user.id,
        cv_data=cv_data,
        avatar=avatar_url
    )
    db.session.add(app)
    db.session.commit()

    return jsonify({"status": "ok", "cv_id": app.id})