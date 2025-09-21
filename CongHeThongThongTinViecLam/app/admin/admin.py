from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
from werkzeug.security import generate_password_hash
from wtforms import PasswordField, SelectField, TextAreaField,StringField
from ..models import db, User, JobPosting, Company, JobType, UserRole, Templates, Province, District, Ward
from markupsafe import Markup
from flask_admin.helpers import get_url
from wtforms import SelectField
from wtforms_sqlalchemy.fields import QuerySelectField

# ------------------- Index View -------------------
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render(
            'admin/index.html',
            users_count=User.query.count(),
            jobs_count=JobPosting.query.count(),
            companies_count=Company.query.count(),
            jobtypes_count=JobType.query.count(),
            templates_count=Templates.query.count()
        )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == UserRole.admin.value

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login-screen'))

# ------------------- Base ModelView -------------------
class AdminModelViewBase(ModelView):
    def __init__(self, model, session, **kwargs):
        if not getattr(self, 'column_list', None):
            self.column_list = [c.name for c in model.__table__.columns] + ['_actions']
        self.column_display_actions = False

        def _actions_formatter(view, context, model, name):
            edit_url = get_url('.edit_view', id=model.id)
            delete_url = get_url('.delete_view', id=model.id)
            return Markup(f'''
                <a class="btn btn-sm btn-primary" href="{edit_url}">
                    <i class="fa fa-edit"></i> Edit
                </a>
                <a class="btn btn-sm btn-danger" href="{delete_url}" onclick="return confirm('Bạn có chắc muốn xóa không?');">
                    <i class="fa fa-trash"></i> Delete
                </a>
            ''')

        self.column_formatters = {
            '_actions': _actions_formatter
        }

        self.column_searchable_list = [
            c.name for c in model.__table__.columns
            if str(c.type) in ('VARCHAR', 'TEXT', 'STRING')
        ]
        self.column_filters = [
            c.name for c in model.__table__.columns
            if str(c.type) in ('VARCHAR', 'TEXT', 'STRING', 'DATE', 'ENUM')
        ]
        super().__init__(model, session, **kwargs)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == UserRole.admin.value

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login-screen'))

    def create_model(self, form):
        try:
            model = self.model()
            self.on_model_change(form, model, True)
            self.session.add(model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            flash(f'Error creating record: {e}', 'error')
            return False

    def update_model(self, form, model):
        try:
            self.on_model_change(form, model, False)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            flash(f'Error updating record: {e}', 'error')
            return False

class UserAdmin(AdminModelViewBase):
    form_excluded_columns = ['comments', 'reports', 'job_postings', 'job_applications']

    # Chỉ định SelectField cho Enum
    form_overrides = {
        'user_type': SelectField,
        'gender': SelectField
    }

    # Chọn giá trị hiển thị cho SelectField
    form_choices = {
        'user_type': [(role.value, role.name.capitalize()) for role in UserRole],
        'gender': [(g.value, g.name.capitalize()) for g in User.__table__.columns
                   if hasattr(User, 'gender') and isinstance(User.gender.type, type(g))]
    }

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.password = PasswordField('Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = generate_password_hash(form.password.data)
        super().on_model_change(form, model, is_created)

# ------------------- JobTypeAdmin -------------------
class JobTypeAdmin(AdminModelViewBase):
    pass

# ------------------- CompanyAdmin -------------------
class CompanyAdmin(AdminModelViewBase):
    form_excluded_columns = ['job_postings']

    form_columns = [
        'company_name', 'company_tax_id', 'business_type', 'company_address',
        'established_date', 'business_status', 'phone_contact', 'legal_representative',
        'province_code', 'district_code', 'ward_code', 'user_id'
    ]

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        if hasattr(form, 'business_status'):
            model.business_status = bool(form.business_status.data)

# ------------------- JobPostingAdmin -------------------
class JobPostingAdmin(AdminModelViewBase):
    column_list = (
        'id', 'job_title', 'job_description', 'requirements', 'benefits',
        'job_type_name', 'salary_range', 'status', 'created_date',
        'expiration_date', 'user_email', 'company_name',
        'province_name', 'district_name', 'ward_name', '_actions'
    )

    form_columns = [
        'job_title', 'job_description', 'benefits',
        'job_type_id', 'salary_range', 'status', 'created_date',
        'expiration_date', 'requirements', 'company_id',
        'province_code', 'district_code', 'ward_code'
    ]

    form_overrides = {
        'province_code': SelectField,
        'district_code': SelectField,
        'ward_code': SelectField,
        'company_id': QuerySelectField,
        'job_type_id': QuerySelectField,
    }

    def create_form(self, obj=None):
        form = super().create_form(obj)
        # Province
        form.province_code.choices = [(p.code, p.full_name) for p in Province.query.order_by(Province.name).all()]

        # District
        if form.province_code.data:
            form.district_code.choices = [(d.code, d.full_name) for d in
                                          District.query.filter_by(province_code=form.province_code.data).order_by(
                                              District.name)]
        else:
            form.district_code.choices = []

        # Ward
        if form.district_code.data:
            form.ward_code.choices = [(w.code, w.full_name) for w in
                                      Ward.query.filter_by(district_code=form.district_code.data).order_by(Ward.name)]
        else:
            form.ward_code.choices = []

        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        # Province
        form.province_code.choices = [(p.code, p.full_name) for p in Province.query.order_by(Province.name).all()]

        # District
        if form.province_code.data:
            form.district_code.choices = [(d.code, d.full_name) for d in
                                          District.query.filter_by(province_code=form.province_code.data).order_by(
                                              District.name)]
        else:
            form.district_code.choices = []

        # Ward
        if form.district_code.data:
            form.ward_code.choices = [(w.code, w.full_name) for w in
                                      Ward.query.filter_by(district_code=form.district_code.data).order_by(Ward.name)]
        else:
            form.ward_code.choices = []

        return form

    def on_model_change(self, form, model, is_created):
        form.populate_obj(model)
        if hasattr(form.job_type_id.data, "id"):
            model.job_type_id = form.job_type_id.data.id
        if hasattr(form.company_id.data, "id"):
            model.company_id = form.company_id.data.id

    form_args = {
        'company_id': {
            'query_factory': lambda: Company.query.all(),
            'get_pk': lambda obj: obj.id,
            'get_label': 'company_name'
        },
        'job_type_id': {
            'query_factory': lambda: JobType.query.all(),
            'get_pk': lambda obj: obj.id,
            'get_label': 'type'
        }
    }

    edit_template = 'admin/job_posting.html'
    create_template = 'admin/job_posting.html'

class TemplatesAdmin(ModelView):
    column_list = ['id', 'name', 'created_at', 'actions']
    form_excluded_columns = ['created_at']

    # Chỉ truyền class, không truyền label
    form_overrides = {
        'background': StringField
    }

    # Nếu muốn đặt label, dùng form_args
    form_args = {
        'background': {'label': 'Background URL'},
        'layout_json': {'label': 'Layout JSON'}
    }

    # Thêm field layout_json
    form_extra_fields = {
        'layout_json': TextAreaField()
    }

    # Preview background trong list view
    def _background_preview(view, context, model, name):
        if model.background:
            return Markup(f'<img src="{model.background}" style="width:100px;height:auto;">')
        return ''

    column_formatters = {
        'background': _background_preview
    }

    def _actions_formatter(view, context, model, name):
        edit_url = get_url('.edit_view', id=model.id)
        return Markup(f'''
            <a class="btn btn-sm btn-info" href="{edit_url}">
                <i class="fa fa-refresh"></i> Tải lại
            </a>
        ''')

    column_formatters = {
        'actions': _actions_formatter
    }

    create_template = 'admin/template.html'
    edit_template = 'admin/template.html'

# ------------------- Init Admin -------------------
def init_admin(app):
    admin = Admin(
        app,
        name="Dashboard Admin",
        template_mode="bootstrap4",
        index_view=MyAdminIndexView()
    )

    admin.add_view(UserAdmin(User, db.session, endpoint='admin_user', category='Management'))
    admin.add_view(JobTypeAdmin(JobType, db.session, endpoint='admin_jobtype', category='Management'))
    admin.add_view(CompanyAdmin(Company, db.session, endpoint='admin_company', category='Management'))
    admin.add_view(JobPostingAdmin(JobPosting, db.session, endpoint='admin_jobposting', category='Management'))
    admin.add_view(TemplatesAdmin(Templates, db.session, endpoint='admin_templates', category='CV'))

    return admin
