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

# routes.py - Thêm endpoint để render CV
@cv_bp.route('/preview/<int:template_id>')
def preview_template(template_id):
    template = Templates.query.get_or_404(template_id)
    
    # Dữ liệu mẫu để preview
    sample_data = {
        'name': 'Nguyễn Văn A',
        'email': 'nguyenvana@example.com',
        'phone': '0123 456 789',
        'objective': 'Mong muốn được làm việc trong môi trường chuyên nghiệp...',
        'experience': [
            {'position': 'Developer', 'company': 'ABC Company', 'period': '2020-2022'},
            {'position': 'Intern', 'company': 'XYZ Corp', 'period': '2019-2020'}
        ],
        # ... thêm các dữ liệu mẫu khác
    }
    
    return render_template('candidate/preview.html', 
                         template=template, 
                         data=sample_data)

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

    app = JobApplication(
        user_id=user.id,
        cv_data=cv_data,
        avatar=avatar_url
    )
    db.session.add(app)
    db.session.commit()

    return jsonify({"status": "ok", "cv_id": app.id})

@cv_bp.route("/my-cvs-screen", methods=["GET"])
@login_required
def my_cvs_screen():
    
    user = current_user
    print(user.id)
    
    cvs = JobApplication.query.filter_by(user_id=user.id).all()
    print(cvs)
    return render_template("candidate/my_cvs.html", cvs=cvs)


@cv_bp.route("/my-cvs/<int:application_id>", methods=["GET"])
@login_required
def view_generated_cv(application_id):
    user = current_user
    app = JobApplication.query.filter_by(id=application_id, user_id=user.id).first_or_404()
    return render_template("candidate/view_cv.html", cv=app)


@cv_bp.route("/my-cvs/<int:application_id>/json", methods=["GET"])
@login_required
def api_cv_detail(application_id):
    user = current_user
    app = JobApplication.query.filter_by(id=application_id, user_id=user.id).first_or_404()

    html_content = render_template("candidate/view_cv.html", cv=app)

    data = {
        "id": app.id,
        "created_at": app.created_at.strftime("%Y-%m-%d %H:%M"),
        "avatar": app.avatar,
        "cv_data": app.cv_data,
        "html": html_content
    }
    return jsonify(data)
