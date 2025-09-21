from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from sqlalchemy.orm import joinedload

from app import db
from app.models import JobPosting, Province, JobType, Company, District, Ward
from flask_login import login_required, current_user

company_bp = Blueprint("company", __name__)

@company_bp.route("/my-jobs")
@login_required
def my_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    jobs_query = JobPosting.query.options(
        joinedload(JobPosting.company),
        joinedload(JobPosting.job_type),
        joinedload(JobPosting.province),
        joinedload(JobPosting.district),
        joinedload(JobPosting.ward)
    ).filter(JobPosting.user_id == current_user.id)
    print(JobPosting.user_id)
    print(current_user.id)

    jobs_pagination = jobs_query.order_by(JobPosting.created_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    jobs = jobs_pagination.items

    return render_template(
        "company/my_jobs.html",
        jobs=jobs,
        pagination=jobs_pagination
    )

@company_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_company():
    company = Company.query.filter_by(user_id=current_user.id).first()
    if not company:
        flash("Bạn chưa tạo thông tin công ty.", "danger")
        return redirect(url_for("profile"))

    provinces = Province.query.order_by(Province.name).all()
    districts = District.query.filter_by(province_code=company.province_code).order_by(District.name).all() if company.province_code else []
    wards = Ward.query.filter_by(district_code=company.district_code).order_by(Ward.name).all() if company.district_code else []

    if request.method == "POST":
        company.company_name = request.form.get("company_name")
        company.company_tax_id = request.form.get("company_tax_id")
        company.business_type = request.form.get("business_type")
        company.company_address = request.form.get("company_address")
        company.established_date = request.form.get("established_date")
        company.business_status = bool(int(request.form.get("business_status")))
        company.phone_contact = request.form.get("phone_contact")
        company.legal_representative = request.form.get("legal_representative")
        company.province_code = request.form.get("province_code")
        company.district_code = request.form.get("district_code")
        company.ward_code = request.form.get("ward_code")

        try:
            db.session.commit()
            flash("Cập nhật thông tin công ty thành công!", "success")
            return redirect(url_for("auth.profile_screen"))
        except Exception as e:
            db.session.rollback()
            flash("Có lỗi khi cập nhật: " + str(e), "danger")

    return render_template(
        "company/edit_company.html",
        company=company,
        provinces=provinces
    )