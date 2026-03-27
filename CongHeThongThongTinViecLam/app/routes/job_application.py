from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user,login_required
from ..models import JobApplication, Templates, UserRole, Application, JobPosting
from flask import abort
from app.extensions import db
from config import upload_avatar
import json
from markupsafe import Markup
cv_bp = Blueprint("cv", __name__, url_prefix="/cv")

@cv_bp.route("/create-form", methods=["GET"])
def create_form():
    return render_template("candidate/CV.html")  

@cv_bp.route('/preview/<int:template_id>')
def preview_template(template_id):
    template = Templates.query.get_or_404(template_id)
    
    
    sample_data = {
        'name': 'Nguyễn Văn A',
        'email': 'nguyenvana@example.com',
        'phone': '0123 456 789',
        'objective': 'Mong muốn được làm việc trong môi trường chuyên nghiệp...',
        'experience': [
            {'position': 'Developer', 'company': 'ABC Company', 'period': '2020-2022'},
            {'position': 'Intern', 'company': 'XYZ Corp', 'period': '2019-2020'}
        ],
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


@cv_bp.route("/update-cv/<int:cv_id>", methods=["PUT"])
@login_required
def update_cv(cv_id):
    try:
        user = current_user
        
        
        cv = JobApplication.query.filter_by(id=cv_id, user_id=user.id).first()
        if not cv:
            return jsonify({"error": "CV không tồn tại hoặc bạn không có quyền chỉnh sửa"}), 404
        
        
        if request.is_json:
            data = request.get_json()
            cv_data = data.get("cv_data")
            
            
            if not cv_data:
                return jsonify({"error": "Thiếu dữ liệu CV"}), 400
                
                
            if isinstance(cv_data, str):
                try:
                    cv_data = json.loads(cv_data)
                except json.JSONDecodeError:
                    return jsonify({"error": "Dữ liệu CV không hợp lệ"}), 400
            elif not isinstance(cv_data, dict):
                return jsonify({"error": "Định dạng dữ liệu không hợp lệ"}), 400
                
        else:
            return jsonify({"error": "Yêu cầu phải là JSON"}), 400
        
        
        cv.cv_data = cv_data
        
        
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "CV đã được cập nhật thành công",
            "cv_id": cv.id,
            "created_at": cv.created_at.strftime("%Y-%m-%d %H:%M:%S") if cv.created_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@cv_bp.route("/delete-cv/<int:cv_id>", methods=["DELETE"])
@login_required
def delete_cv(cv_id):
    user = current_user
    
    
    cv = JobApplication.query.filter_by(id=cv_id, user_id=user.id).first_or_404()
    
    
    applications = Application.query.filter_by(cv_id=cv_id).first()
    if applications:
        return jsonify({
            "error": "Không thể xóa CV này vì nó đang được sử dụng trong đơn ứng tuyển"
        }), 400
    
    
    db.session.delete(cv)
    db.session.commit()
    
    return jsonify({
        "status": "success", 
        "message": "CV đã được xóa thành công"
    })


@cv_bp.route("/duplicate-cv/<int:cv_id>", methods=["POST"])
@login_required
def duplicate_cv(cv_id):
    user = current_user
    
    
    original_cv = JobApplication.query.filter_by(id=cv_id, user_id=user.id).first_or_404()
    
    
    new_cv = JobApplication(
        user_id=user.id,
        cv_data=original_cv.cv_data,
        avatar=original_cv.avatar 
    )
    
    db.session.add(new_cv)
    db.session.commit()
    
    return jsonify({
        "status": "success", 
        "message": "CV đã được sao chép thành công",
        "new_cv_id": new_cv.id
    })


@cv_bp.route("/edit-cv/<int:cv_id>", methods=["GET"])
@login_required
def get_cv_for_edit(cv_id):
    user = current_user
    
    
    cv = JobApplication.query.filter_by(id=cv_id, user_id=user.id).first_or_404()
    
    return jsonify({
        "id": cv.id,
        "avatar": cv.avatar,
        "cv_data": cv.cv_data,
        "created_at": cv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        
    })


@cv_bp.route("/edit-cv-screen/<int:cv_id>", methods=["GET"])
@login_required
def edit_cv_screen(cv_id):
    user = current_user
    
    
    cv = JobApplication.query.filter_by(id=cv_id, user_id=user.id).first_or_404()
    
    return render_template("candidate/update_cv.html", cv=cv)

@cv_bp.route("/my-cvs-screen", methods=["GET"])
@login_required
def my_cvs_screen():
    user = current_user
    cvs = JobApplication.query.filter_by(user_id=user.id).order_by(JobApplication.created_at.desc()).all()
    return render_template("candidate/my_cvs.html", cvs=cvs)

@cv_bp.route("/my-cvs/<int:application_id>", methods=["GET"])
@login_required
def view_generated_cv(application_id):
    user = current_user


    if user.user_type == UserRole.candidate.value:
        app = JobApplication.query.filter_by(id=application_id, user_id=user.id).first_or_404()


    elif user.user_type == UserRole.approver.value:
        app = (
            JobApplication.query.join(Application)
            .join(Application.job_posting)
            .filter(
                JobApplication.id == application_id,
                JobPosting.user_id == user.id  
            )
            .first()
        )
        if not app:
            abort(404)


    elif user.user_type == UserRole.admin.value:
        app = JobApplication.query.get_or_404(application_id)

    else:
        abort(403)  

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
        "updated_at": app.updated_at.strftime("%Y-%m-%d %H:%M") if app.updated_at else None,
        "avatar": app.avatar,
        "cv_data": app.cv_data,
        "html": html_content
    }
    return jsonify(data)

@cv_bp.route("/select/<int:job_id>", methods=["GET"])
@login_required
def select_cv(job_id):
    cvs = JobApplication.query.filter_by(user_id=current_user.id).all()
    return render_template("candidate/select_cv.html", cvs=cvs, job_id=job_id)