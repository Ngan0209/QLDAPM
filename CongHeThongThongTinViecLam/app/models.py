from .extensions import  db
from enum import Enum as RoleEnum
from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, Boolean, Float,UniqueConstraint
from flask_login import UserMixin
from sqlalchemy.types import Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects import postgresql
from datetime import datetime
class UserRole(RoleEnum):
    admin = "admin"
    candidate = "candidate"
    approver = "approver"


class User(UserMixin,db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    firstname = db.Column(db.String(200))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    user_type = db.Column(db.String(20), default=UserRole.candidate.value)
    dob = db.Column(db.Date)
    avatar = db.Column(db.String(255))

    comments = db.relationship("Comment", backref="user", lazy=True)
    reports = db.relationship("Report", backref="user", lazy=True)
    job_postings = db.relationship("JobPosting", backref="user", lazy=True)
    job_applications = db.relationship("JobApplication", backref="job_application_user", lazy=True)


class JobType(db.Model):
    __tablename__ = "job_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), unique=True)
    job_postings = db.relationship("JobPosting", backref="job_type", lazy=True)


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

    job_postings = db.relationship("JobPosting", backref="company", lazy=True)


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

    # thêm quan hệ hành chính
    province_code = db.Column(db.String(20), db.ForeignKey("provinces.code"))
    district_code = db.Column(db.String(20), db.ForeignKey("districts.code"))
    ward_code = db.Column(db.String(20), db.ForeignKey("wards.code"))

    comments = db.relationship("Comment", backref="job_posting", lazy=True)
    reports = db.relationship("Report", backref="job_posting", lazy=True)
    requirements = db.relationship("JobRequire", backref="job_posting", lazy=True)
    applications = db.relationship("Application", backref="job_posting", lazy=True)


class JobRequire(db.Model):
    __tablename__ = "job_require"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(100))
    post_id = db.Column(db.Integer, db.ForeignKey("job_posting.id"))


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)


    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("job_posting.id"))



class Report(db.Model):
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.Date)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("job_posting.id"))


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
    avatar = db.Column(db.String(255), nullable = True)


    applications = db.relationship("Application", backref="job_application", lazy=True)






class Application(db.Model):
    __tablename__ = "application"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(50))
    update_date = db.Column(db.Date)


    job_application_id = db.Column(db.Integer, db.ForeignKey("job_application.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("job_posting.id"))

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

    provinces = db.relationship("Province", backref="administrative_region", lazy=True)


class AdministrativeUnit(db.Model):
    __tablename__ = "administrative_units"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    full_name_en = db.Column(db.String(255))
    short_name = db.Column(db.String(255))
    short_name_en = db.Column(db.String(255))
    code_name = db.Column(db.String(255))
    code_name_en = db.Column(db.String(255))

    provinces = db.relationship("Province", backref="administrative_unit", lazy=True)
    districts = db.relationship("District", backref="administrative_unit", lazy=True)
    wards = db.relationship("Ward", backref="administrative_unit", lazy=True)


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

    districts = db.relationship("District", backref="province", lazy=True)
    job_postings = db.relationship("JobPosting", backref="province", lazy=True)  
    companies = db.relationship("Company", backref="province", lazy=True)  


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

    wards = db.relationship("Ward", backref="district", lazy=True)
    job_postings = db.relationship("JobPosting", backref="district", lazy=True)  
    companies = db.relationship("Company", backref="district", lazy=True)  


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

    job_postings = db.relationship("JobPosting", backref="ward", lazy=True) 
    companies = db.relationship("Company", backref="ward", lazy=True)  

