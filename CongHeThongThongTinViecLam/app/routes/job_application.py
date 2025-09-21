from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user,login_required
from ..models import JobApplication, Templates
from app.extensions import db
from config import upload_avatar
import json
from markupsafe import Markup
cv_bp = Blueprint("cv", __name__, url_prefix="/cv")

@cv_bp.route("/create-form", methods=["GET"])
def create_form():
    return render_template("candidate/CV.html")  

# @cv_bp.route("/templates", methods=["GET"])
# def get_templates():
#     templates = Templates.query.order_by(Templates.created_at.desc()).all()
#     print(templates)
#     data = [
#         {
#             "id": t.id,
#             "name": t.name,
#             "background": t.background,
#             "layout_json": t.layout_json,
#             "created_at": t.created_at.isoformat()
#         }
#         for t in templates
#     ]
    
#     return jsonify(data), 200

@cv_bp.route("/templates-screen", methods=["GET"])
def templates_screen():
    templates = Templates.query.order_by(Templates.created_at.desc()).all()
    templates_json = json.dumps([
        {
            "id": t.id,
            "name": t.name,
            "background": t.background,
            "layout_json": t.layout_json,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for t in templates
    ])
    return render_template(
        "candidate/templates.html",
        templates=templates,
        templates_json=Markup(templates_json)
    )

@cv_bp.route("/templates/<int:template_id>", methods=["GET"])
def get_template_detail(template_id):
    template = Templates.query.get_or_404(template_id)
    return render_template("candidate/template_detail.html", template=template)

@cv_bp.route("/create-cv", methods=["POST"])
@login_required
def create_cv():
    user = current_user

    cv_data_str = request.form.get("cv_data")
    if not cv_data_str:
        return jsonify({"error": "Missing cv_data"}), 400

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