from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
from werkzeug.security import generate_password_hash
from wtforms import PasswordField, SelectField, TextAreaField,StringField
from ..models import db, User, JobPosting, Company, JobType, UserRole, Templates
from markupsafe import Markup
from flask_admin.helpers import get_url

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
        self.column_list = [c.name for c in model.__table__.columns]
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
            form.populate_obj(model)
            self.session.add(model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            flash(f'Error creating record: {e}', 'error')
            return False

    def update_model(self, form, model):
        try:
            form.populate_obj(model)
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

    def on_model_change(self, form, model, is_created):
        super().on_model_change(form, model, is_created)
        if hasattr(form, 'business_status'):
            model.business_status = bool(form.business_status.data)

# ------------------- JobPostingAdmin -------------------
class JobPostingAdmin(AdminModelViewBase):
    form_excluded_columns = ['comments', 'reports', 'requirements', 'applications']

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
