from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from app.badwords import check_content
from app.extensions import db
from app.models import JobPosting, Province, JobType
import datetime

job_posting_bp = Blueprint("job", __name__, url_prefix="/job")

@job_posting_bp.route("/<int:job_id>")
def detail(job_id):
    job = JobPosting.query.options(
        joinedload(JobPosting.company),
        joinedload(JobPosting.job_type),
        joinedload(JobPosting.province),
        joinedload(JobPosting.district),
        joinedload(JobPosting.ward)
    ).get_or_404(job_id)
    return render_template("job_detail.html", job=job)

@job_posting_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    user = current_user

    if user.user_type != "approver":
        flash("Bạn không có quyền đăng tin tuyển dụng.", "danger")
        return redirect(url_for("home.index"))

    company = user.company
    provinces = Province.query.order_by(Province.name).all()
    job_types = JobType.query.order_by(JobType.id).all()

    company_province = company.province_code if company and company.province_code else ""
    company_district = company.district_code if company and company.district_code else ""
    company_ward = company.ward_code if company and company.ward_code else ""

    if request.method == "POST":
        # Xử lý lương
        if request.form.get("salary_negotiable"):
            salary_range = "Thỏa thuận"
        else:
            salary_from = request.form.get("salary_from")
            salary_to = request.form.get("salary_to")
            if salary_from and salary_to:
                salary_range = f"{salary_from} - {salary_to}"
            elif salary_from:
                salary_range = f"Trên {salary_from}"
            else:
                salary_range = ""

        fields_to_check = [
            request.form.get("job_title", ""),
            request.form.get("job_description", ""),
            request.form.get("requirements", ""),
            request.form.get("benefits", "")
        ]
        for field in fields_to_check:
            if field and check_content(field):
                flash("Bài đăng chứa từ ngữ không phù hợp. Vui lòng kiểm tra lại.", "danger")
                return render_template(
                    "company/job_posting.html",
                    company=company,
                    provinces=provinces,
                    job_types=job_types,
                    company_province=company_province,
                    company_district=company_district,
                    company_ward=company_ward,
                    form_data=request.form
                )

        job = JobPosting(
            job_title        = request.form.get("job_title"),
            job_description  = request.form.get("job_description"),
            requirements     = request.form.get("requirements"),
            benefits         = request.form.get("benefits"),
            job_type_id      = request.form.get("job_type_id"),
            salary_range     = salary_range,
            status           = "active",
            created_date     = datetime.date.today(),
            expiration_date  = request.form.get("expiration_date"),
            user_id          = user.id,
            company_id       = company.id if company else None,
            province_code    = request.form.get("province_code"),
            district_code    = request.form.get("district_code"),
            ward_code        = request.form.get("ward_code"),
        )
        db.session.add(job)
        db.session.commit()
        flash("Đăng tin thành công!", "success")
        return redirect(url_for("home.index"))

    return render_template(
        "company/job_posting.html",
        company=company,
        provinces=provinces,
        job_types=job_types,
        company_province=company_province,
        company_district=company_district,
        company_ward=company_ward,
        form_data=None
    )

@job_posting_bp.route("/edit/<int:job_id>", methods=["GET", "POST"])
@login_required
def edit(job_id):
    job = JobPosting.query.get_or_404(job_id)
    user = current_user

    is_owner = (job.user_id == user.id)
    is_company_approver = (
            user.user_type == "approver"
            and user.company
            and job.company_id == user.company.id
    )

    if not (is_owner or is_company_approver):
        flash("Bạn không có quyền chỉnh sửa tin này.", "danger")
        return redirect(url_for("job.detail", job_id=job.id))

    company = user.company
    provinces = Province.query.order_by(Province.name).all()
    job_types = JobType.query.order_by(JobType.id).all()

    company_province = job.province_code or (company.province_code if company else "")
    company_district = job.district_code or (company.district_code if company else "")
    company_ward = job.ward_code or (company.ward_code if company else "")

    if request.method == "POST":
        if request.form.get("salary_negotiable"):
            salary_range = "Thỏa thuận"
        else:
            salary_from = request.form.get("salary_from")
            salary_to = request.form.get("salary_to")
            if salary_from and salary_to:
                salary_range = f"{salary_from} - {salary_to}"
            elif salary_from:
                salary_range = f"Trên {salary_from}"
            else:
                salary_range = ""

        fields_to_check = [
            request.form.get("job_title", ""),
            request.form.get("job_description", ""),
            request.form.get("requirements", ""),
            request.form.get("benefits", "")
        ]
        for field in fields_to_check:
            if field and check_content(field):
                flash("Bài đăng chứa từ ngữ không phù hợp. Vui lòng kiểm tra lại.", "danger")
                return render_template(
                    "company/job_posting.html",
                    edit_mode=True,
                    job=job,
                    company=company,
                    provinces=provinces,
                    job_types=job_types,
                    company_province=company_province,
                    company_district=company_district,
                    company_ward=company_ward,
                    form_data=request.form
                )

        job.job_title = request.form.get("job_title")
        job.job_description = request.form.get("job_description")
        job.requirements = request.form.get("requirements")
        job.benefits = request.form.get("benefits")
        job.job_type_id = request.form.get("job_type_id")
        job.salary_range = salary_range
        job.expiration_date = request.form.get("expiration_date")
        job.province_code = request.form.get("province_code")
        job.district_code = request.form.get("district_code")
        job.ward_code = request.form.get("ward_code")

        db.session.commit()
        flash("Cập nhật tin thành công!", "success")
        return redirect(url_for("job.detail", job_id=job.id))

    return render_template(
        "company/job_posting.html",
        edit_mode=True,
        job=job,
        company=company,
        provinces=provinces,
        job_types=job_types,
        company_province=company_province,
        company_district=company_district,
        company_ward=company_ward,
        form_data=None
    )

@job_posting_bp.route("/delete/<int:job_id>", methods=["POST"])
@login_required
def delete(job_id):
    job = JobPosting.query.get_or_404(job_id)
    user = current_user

    is_owner = (job.user_id == user.id)
    is_company_approver = (
        user.user_type == "approver"
        and user.company
        and job.company_id == user.company.id
    )

    if not (is_owner or is_company_approver):
        flash("Bạn không có quyền xóa bài đăng này.", "danger")
        return redirect(url_for("job.detail", job_id=job.id))

    db.session.delete(job)
    db.session.commit()
    flash("Đã xóa bài đăng thành công!", "success")
    return redirect(url_for("employer.my_jobs"))