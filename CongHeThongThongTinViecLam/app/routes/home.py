from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import case, cast, Integer, or_
import json
import re
from app.models import JobPosting, Province, JobType, District, Ward, User

home_bp = Blueprint("home", __name__)

def parse_salary_range(salary_range_str):
    if not salary_range_str:
        return None, None
    nums = re.findall(r'\d+', salary_range_str)
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    elif len(nums) == 1:
        return int(nums[0]), int(nums[0])
    return None, None

class ManualPagination:
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total // per_page) + (1 if total % per_page else 0)
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1
        self.next_num = page + 1

@home_bp.route("/", endpoint="index")
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    q = request.args.get('q', '').strip()
    province_code = request.args.get('province_code', '')
    job_type_id = request.args.get('job_type_id', '')
    district_codes = request.args.getlist('district_code')
    salary_filter = request.args.get('salary_filter', '')

    query = JobPosting.query.options(
        joinedload(JobPosting.company),
        joinedload(JobPosting.job_type),
        joinedload(JobPosting.province),
        joinedload(JobPosting.district),
        joinedload(JobPosting.ward)
    )

    if q:
        query = query.filter(
            or_(
                JobPosting.job_title.ilike(f"%{q}%"),
                JobPosting.job_description.ilike(f"%{q}%"),
                JobPosting.requirements.ilike(f"%{q}%"),
                JobPosting.benefits.ilike(f"%{q}%"),
                JobPosting.company.has(company_name=q)
            )
        )

    if province_code:
        query = query.filter(JobPosting.province_code == province_code)

    if job_type_id:
        query = query.filter(JobPosting.job_type_id == job_type_id)

    if district_codes:
        query = query.filter(JobPosting.district_code.in_(district_codes))

    province_selected = None
    if province_code:
        province_selected = Province.query.filter_by(code=province_code).first()

    districts_selected = []
    if district_codes:
        from app.models import District
        districts_selected = District.query.filter(District.code.in_(district_codes)).all()

    jobs = query.order_by(JobPosting.created_date.desc()).all()

    if salary_filter:
        filtered_jobs = []
        for job in jobs:
            min_sal, max_sal = parse_salary_range(job.salary_range)
            if min_sal is None or max_sal is None:
                continue
            if salary_filter == 'lt10' and max_sal < 10_000_000:
                filtered_jobs.append(job)
            elif salary_filter == '10-15' and max_sal >= 10_000_000 and min_sal <= 15_000_000:
                filtered_jobs.append(job)
            elif salary_filter == '15-20' and max_sal >= 15_000_000 and min_sal <= 20_000_000:
                filtered_jobs.append(job)
            elif salary_filter == '20-30' and max_sal >= 20_000_000 and min_sal <= 30_000_000:
                filtered_jobs.append(job)
            elif salary_filter == 'gt30' and min_sal > 30_000_000:
                filtered_jobs.append(job)
        jobs = filtered_jobs

    # Phân trang thủ công
    total = len(jobs)
    start = (page-1)*per_page
    end = start + per_page
    jobs_page = jobs[start:end]

    # Tạo pagination thủ công
    pagination = ManualPagination(jobs_page, page, per_page, total)

    provinces = Province.query.order_by(Province.name).all()
    job_types = JobType.query.order_by(JobType.id).all()
    provinces_json = json.dumps([{"code": p.code, "name": p.name} for p in provinces], ensure_ascii=False)

    return render_template(
        "home.html",
        jobs=jobs_page,
        pagination=pagination,
        provinces=provinces,
        job_types=job_types,
        provinces_json=provinces_json,
        province_selected=province_selected,
        districts_selected=districts_selected
    )

@home_bp.route("/api/districts")
@login_required
def api_districts():
    province_code = request.args.get("province_code")
    districts = District.query.filter_by(province_code=province_code).order_by(
        case(
            (District.name.op('regexp')('^[0-9]+$'), 0),
            else_=1
        ),
        cast(District.name, Integer),
        District.name
    ).all()
    return jsonify([{"code": d.code, "name": d.full_name} for d in districts])

@home_bp.route("/api/wards")
@login_required
def api_wards():
    district_code = request.args.get("district_code")
    wards = Ward.query.filter_by(district_code=district_code).order_by(
        case(
            (Ward.name.op('regexp')('^[0-9]+$'), 0),
            else_=1
        ),
        cast(Ward.name, Integer),
        Ward.name
    ).all()
    return jsonify([{"code": w.code, "name": w.full_name} for w in wards])

@home_bp.route('/api/company_users')
@login_required
def get_company_users():
    if not hasattr(current_user, 'role') or current_user.user_type != 'admin':
        abort(403)

    company_id = request.args.get("company_id")
    users = User.query.filter_by(company_id=company_id).all()
    return jsonify([{"id": u.id, "email": u.email} for u in users])