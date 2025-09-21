from .extensions import db
from enum import Enum as RoleEnum
from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, Boolean, Float, UniqueConstraint
from flask_login import UserMixin
from sqlalchemy.types import Text
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class UserRole(RoleEnum):
    admin = "admin"
    candidate = "candidate"
    approver = "approver"

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(200))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    user_type = db.Column(db.String(20), default=UserRole.candidate.value)
    dob = db.Column(db.Date)
    avatar = db.Column(db.String(255))

    # Quan hệ 1-1 với Company
    company = db.relationship("Company", back_populates="user", uselist=False)
    comments = db.relationship("Comment", back_populates="user", lazy=True)
    reports = db.relationship("Report", back_populates="user", lazy=True)
    job_postings = db.relationship("JobPosting", back_populates="user", lazy=True)
    job_applications = db.relationship("JobApplication", back_populates="user", lazy=True)

class JobType(db.Model):
    __tablename__ = "job_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), unique=True)
    job_postings = db.relationship("JobPosting", back_populates="job_type", lazy=True)

class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_tax_id = db.Column(db.String(50), unique=True)
    business_type = db.Column(db.String(50))
    company_address = db.Column(db.String(200))
    established_date = db.Column(db.Date)
    business_status = db.Column(db.Boolean, default=True)
    phone_contact = db.Column(db.String(20), unique=True)
    legal_representative = db.Column(db.String(100))

    province_code = db.Column(db.String(20), db.ForeignKey("provinces.code"))
    district_code = db.Column(db.String(20), db.ForeignKey("districts.code"))
    ward_code = db.Column(db.String(20), db.ForeignKey("wards.code"))

    # Thêm khóa ngoại user_id, unique để đảm bảo 1-1
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    user = db.relationship("User", back_populates="company", uselist=False)
    job_postings = db.relationship("JobPosting", back_populates="company", lazy=True)
    province = db.relationship("Province", back_populates="companies", lazy="joined")
    district = db.relationship("District", back_populates="companies", lazy="joined")
    ward = db.relationship("Ward", back_populates="companies", lazy="joined")

    @property
    def user_name(self):
        return self.user.username if self.user else ""
    @property
    def province_name(self):
        return self.province.full_name if self.province else '—'

    @property
    def district_name(self):
        return self.district.full_name if self.district else '—'

    @property
    def ward_name(self):
        return self.ward.full_name if self.ward else '—'
    @property
    def status(self):
        return "Hoạt động" if self.business_status else "Ngừng hoạt động"

class JobPosting(db.Model):
    __tablename__ = "job_posting"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text)
    benefits = db.Column(db.Text)
    job_type_id = db.Column(db.Integer, db.ForeignKey("job_type.id"))
    salary_range = db.Column(db.String(50))
    status = db.Column(db.String(20))
    created_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))

    province_code = db.Column(db.String(20), db.ForeignKey("provinces.code"))
    district_code = db.Column(db.String(20), db.ForeignKey("districts.code"))
    ward_code = db.Column(db.String(20), db.ForeignKey("wards.code"))
    requirements = db.Column(db.Text)

    comments = db.relationship("Comment", back_populates="job_posting", lazy=True)
    reports = db.relationship("Report", back_populates="job_posting", lazy=True)
    applications = db.relationship("Application", back_populates="job_posting", lazy=True)

    job_type = db.relationship("JobType", back_populates="job_postings", lazy="joined")
    company = db.relationship("Company", back_populates="job_postings", lazy="joined")
    user = db.relationship("User", back_populates="job_postings", lazy="joined")
    province = db.relationship("Province", back_populates="job_postings", lazy="joined")
    district = db.relationship("District", back_populates="job_postings", lazy="joined")
    ward = db.relationship("Ward", back_populates="job_postings", lazy="joined")

    @property
    def company_name(self):
        return self.company.company_name if self.company else '—'

    @property
    def user_email(self):
        return self.user.email if self.user else '—'

    @property
    def job_type_name(self):
        return self.job_type.type if self.job_type else '—'

    @property
    def province_name(self):
        return self.province.full_name if self.province else '—'

    @property
    def district_name(self):
        return self.district.full_name if self.district else '—'

    @property
    def ward_name(self):
        return self.ward.full_name if self.ward else '—'

class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("job_posting.id"))
    user = db.relationship("User", back_populates="comments", lazy="joined")
    job_posting = db.relationship("JobPosting", back_populates="comments", lazy="joined")

class Report(db.Model):
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("job_posting.id"))
    user = db.relationship("User", back_populates="reports", lazy="joined")
    job_posting = db.relationship("JobPosting", back_populates="reports", lazy="joined")

class Templates(db.Model):
    __tablename__ = "templates"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    background = db.Column(db.String(255), nullable=True)  # URL hoặc path ảnh background
    layout_json = db.Column(db.JSON, nullable=True)       # layout Gridstack JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobApplication(db.Model):
    __tablename__ = "job_application"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cv_data = db.Column(JSON, nullable=False)
    design = db.Column(JSON, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    avatar = db.Column(db.String(255), nullable=True)
    user = db.relationship("User", back_populates="job_applications", lazy="joined")
    applications = db.relationship("Application", back_populates="job_application", lazy=True)

class Application(db.Model):
    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(50))
    update_date = db.Column(db.Date)
    job_application_id = db.Column(db.Integer, db.ForeignKey("job_application.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("job_posting.id"))
    job_application = db.relationship("JobApplication", back_populates="applications", lazy="joined")
    job_posting = db.relationship("JobPosting", back_populates="applications", lazy="joined")
    __table_args__ = (
        UniqueConstraint('job_application_id', 'post_id', name='uix_job_post'),
    )

class AdministrativeRegion(db.Model):
    __tablename__ = "administrative_regions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255), nullable=False)
    code_name = db.Column(db.String(255))
    code_name_en = db.Column(db.String(255))
    provinces = db.relationship("Province", back_populates="administrative_region", lazy=True)

class AdministrativeUnit(db.Model):
    __tablename__ = "administrative_units"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    full_name_en = db.Column(db.String(255))
    short_name = db.Column(db.String(255))
    short_name_en = db.Column(db.String(255))
    code_name = db.Column(db.String(255))
    code_name_en = db.Column(db.String(255))
    provinces = db.relationship("Province", back_populates="administrative_unit", lazy=True)
    districts = db.relationship("District", back_populates="administrative_unit", lazy=True)
    wards = db.relationship("Ward", back_populates="administrative_unit", lazy=True)

class Province(db.Model):
    __tablename__ = "provinces"
    code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255))
    full_name = db.Column(db.String(255), nullable=False)
    full_name_en = db.Column(db.String(255))
    code_name = db.Column(db.String(255))
    administrative_unit_id = db.Column(db.Integer, db.ForeignKey("administrative_units.id"))
    administrative_region_id = db.Column(db.Integer, db.ForeignKey("administrative_regions.id"))
    districts = db.relationship("District", back_populates="province", lazy=True)
    job_postings = db.relationship("JobPosting", back_populates="province", lazy=True)
    companies = db.relationship("Company", back_populates="province", lazy=True)
    administrative_unit = db.relationship("AdministrativeUnit", back_populates="provinces", lazy="joined")
    administrative_region = db.relationship("AdministrativeRegion", back_populates="provinces", lazy="joined")

class District(db.Model):
    __tablename__ = "districts"
    code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    full_name_en = db.Column(db.String(255))
    code_name = db.Column(db.String(255))
    province_code = db.Column(db.String(20), db.ForeignKey("provinces.code"))
    administrative_unit_id = db.Column(db.Integer, db.ForeignKey("administrative_units.id"))
    wards = db.relationship("Ward", back_populates="district", lazy=True)
    job_postings = db.relationship("JobPosting", back_populates="district", lazy=True)
    companies = db.relationship("Company", back_populates="district", lazy=True)
    province = db.relationship("Province", back_populates="districts", lazy="joined")
    administrative_unit = db.relationship("AdministrativeUnit", back_populates="districts", lazy="joined")

class Ward(db.Model):
    __tablename__ = "wards"
    code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    full_name_en = db.Column(db.String(255))
    code_name = db.Column(db.String(255))
    district_code = db.Column(db.String(20), db.ForeignKey("districts.code"))
    administrative_unit_id = db.Column(db.Integer, db.ForeignKey("administrative_units.id"))
    job_postings = db.relationship("JobPosting", back_populates="ward", lazy=True)
    companies = db.relationship("Company", back_populates="ward", lazy=True)
    district = db.relationship("District", back_populates="wards", lazy="joined")
    administrative_unit = db.relationship("AdministrativeUnit", back_populates="wards", lazy="joined")