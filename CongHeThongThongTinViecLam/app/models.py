from datetime import datetime
from enum import Enum as RoleEnum

from flask_login import UserMixin
from sqlalchemy import (
    Column, Integer, String, Enum, Date, ForeignKey, Boolean,
    Float, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.types import Text

from .extensions import db


class UserRole(RoleEnum):
    admin = "admin"
    candidate = "candidate"
    approver = "approver"

class ApplicationStatus(RoleEnum):
    PENDING = "Chờ xác nhận"
    REVIEWED = "Đang kiểm duyệt"
    ACCEPTED = "Đã chấp nhận"
    REJECTED = "Từ chối"


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    firstname = Column(String(200))
    lastname = Column(String(50))
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(20))
    user_type = Column(String(20), default=UserRole.candidate.value)
    dob = Column(Date)
    avatar = Column(String(255))

    company = db.relationship("Company", back_populates="user", uselist=False)
    comments = db.relationship("Comment", back_populates="user", lazy=True)
    reports = db.relationship("Report", back_populates="user", lazy=True)
    job_postings = db.relationship("JobPosting", back_populates="user", lazy=True)
    job_applications = db.relationship("JobApplication", back_populates="user", lazy=True)


class JobType(db.Model):
    __tablename__ = "job_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), unique=True)

    job_postings = db.relationship("JobPosting", back_populates="job_type", lazy=True)


class Company(db.Model):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(100), nullable=False)
    company_tax_id = Column(String(50), unique=True)
    business_type = Column(String(50))
    company_address = Column(String(200))
    established_date = Column(Date)
    business_status = Column(Boolean, default=True)
    phone_contact = Column(String(20), unique=True)
    legal_representative = Column(String(100))

    province_code = Column(String(20), ForeignKey("provinces.code"))
    district_code = Column(String(20), ForeignKey("districts.code"))
    ward_code = Column(String(20), ForeignKey("wards.code"))

    user_id = Column(Integer, ForeignKey("user.id"), unique=True)
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
        return self.province.full_name if self.province else "—"

    @property
    def district_name(self):
        return self.district.full_name if self.district else "—"

    @property
    def ward_name(self):
        return self.ward.full_name if self.ward else "—"

    @property
    def status(self):
        return "Hoạt động" if self.business_status else "Ngừng hoạt động"


class JobPosting(db.Model):
    __tablename__ = "job_posting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String(100), nullable=False)
    job_description = Column(Text)
    benefits = Column(Text)
    job_type_id = Column(Integer, ForeignKey("job_type.id"))
    salary_range = Column(String(50))
    status = Column(String(20))
    created_date = Column(Date)
    expiration_date = Column(Date)

    user_id = Column(Integer, ForeignKey("user.id"))
    company_id = Column(Integer, ForeignKey("company.id"))

    province_code = Column(String(20), ForeignKey("provinces.code"))
    district_code = Column(String(20), ForeignKey("districts.code"))
    ward_code = Column(String(20), ForeignKey("wards.code"))
    requirements = Column(Text)

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
        return self.company.company_name if self.company else "—"

    @property
    def user_email(self):
        return self.user.email if self.user else "—"

    @property
    def job_type_name(self):
        return self.job_type.type if self.job_type else "—"

    @property
    def province_name(self):
        return self.province.full_name if self.province else "—"

    @property
    def district_name(self):
        return self.district.full_name if self.district else "—"

    @property
    def ward_name(self):
        return self.ward.full_name if self.ward else "—"


class Comment(db.Model):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("user.id"))
    post_id = Column(Integer, ForeignKey("job_posting.id"))

    user = db.relationship("User", back_populates="comments", lazy="joined")
    job_posting = db.relationship("JobPosting", back_populates="comments", lazy="joined")


class Report(db.Model):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    description = Column(Text)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey("user.id"))
    post_id = Column(Integer, ForeignKey("job_posting.id"))

    user = db.relationship("User", back_populates="reports", lazy="joined")
    job_posting = db.relationship("JobPosting", back_populates="reports", lazy="joined")



class Templates(db.Model):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    layout_json = Column(Text, nullable=False, default="[]")
    background = Column(String(255))
    thumbnail = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(db.DateTime, default=datetime.utcnow)
    updated_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    color_scheme = Column(Text, default="{}")
    widget_config = Column(Text, default="{}")
    font_family = Column(String(100), default="Arial, sans-serif")
    font_size = Column(String(20), default="14px")

    def __repr__(self):
        return f"<Template {self.name}>"


class JobApplication(db.Model):
    __tablename__ = "job_application"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_data = Column(JSON, nullable=False)
    design = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    avatar = Column(String(255), nullable=True)
    created_at = Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="job_applications", lazy="joined")
    applications = db.relationship("Application", back_populates="job_application", lazy=True)


class Application(db.Model):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.PENDING,
        nullable=False
    )
    update_date = Column(Date)
    job_application_id = Column(Integer, ForeignKey("job_application.id"))
    post_id = Column(Integer, ForeignKey("job_posting.id"))

    job_application = db.relationship("JobApplication", back_populates="applications", lazy="joined")
    job_posting = db.relationship("JobPosting", back_populates="applications", lazy="joined")

    __table_args__ = (
        UniqueConstraint("job_application_id", "post_id", name="uix_job_post"),
    )


class AdministrativeRegion(db.Model):
    __tablename__ = "administrative_regions"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    code_name = Column(String(255))
    code_name_en = Column(String(255))

    provinces = db.relationship("Province", back_populates="administrative_region", lazy=True)


class AdministrativeUnit(db.Model):
    __tablename__ = "administrative_units"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255))
    full_name_en = Column(String(255))
    short_name = Column(String(255))
    short_name_en = Column(String(255))
    code_name = Column(String(255))
    code_name_en = Column(String(255))

    provinces = db.relationship("Province", back_populates="administrative_unit", lazy=True)
    districts = db.relationship("District", back_populates="administrative_unit", lazy=True)
    wards = db.relationship("Ward", back_populates="administrative_unit", lazy=True)


class Province(db.Model):
    __tablename__ = "provinces"

    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    full_name = Column(String(255), nullable=False)
    full_name_en = Column(String(255))
    code_name = Column(String(255))

    administrative_unit_id = Column(Integer, ForeignKey("administrative_units.id"))
    administrative_region_id = Column(Integer, ForeignKey("administrative_regions.id"))

    districts = db.relationship("District", back_populates="province", lazy=True)
    job_postings = db.relationship("JobPosting", back_populates="province", lazy=True)
    companies = db.relationship("Company", back_populates="province", lazy=True)

    administrative_unit = db.relationship("AdministrativeUnit", back_populates="provinces", lazy="joined")
    administrative_region = db.relationship("AdministrativeRegion", back_populates="provinces", lazy="joined")


class District(db.Model):
    __tablename__ = "districts"

    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    full_name = Column(String(255))
    full_name_en = Column(String(255))
    code_name = Column(String(255))

    province_code = Column(String(20), ForeignKey("provinces.code"))
    administrative_unit_id = Column(Integer, ForeignKey("administrative_units.id"))

    wards = db.relationship("Ward", back_populates="district", lazy=True)
    job_postings = db.relationship("JobPosting", back_populates="district", lazy=True)
    companies = db.relationship("Company", back_populates="district", lazy=True)

    province = db.relationship("Province", back_populates="districts", lazy="joined")
    administrative_unit = db.relationship("AdministrativeUnit", back_populates="districts", lazy="joined")


class Ward(db.Model):
    __tablename__ = "wards"

    code = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    full_name = Column(String(255))
    full_name_en = Column(String(255))
    code_name = Column(String(255))

    district_code = Column(String(20), ForeignKey("districts.code"))
    administrative_unit_id = Column(Integer, ForeignKey("administrative_units.id"))

    job_postings = db.relationship("JobPosting", back_populates="ward", lazy=True)
    companies = db.relationship("Company", back_populates="ward", lazy=True)

    district = db.relationship("District", back_populates="wards", lazy="joined")
    administrative_unit = db.relationship("AdministrativeUnit", back_populates="wards", lazy="joined")
