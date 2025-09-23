from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
import json
from flask import redirect, url_for, flash
from werkzeug.security import generate_password_hash
from wtforms import PasswordField, SelectField, TextAreaField, StringField
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
    # Ẩn mật khẩu + các quan hệ khác
    form_excluded_columns = [
        'password', 'comments', 'reports', 'job_postings', 'job_applications'
    ]

    column_exclude_list = ['password']  # Ẩn mật khẩu khỏi list view
    column_details_exclude_list = ['password']  # Ẩn mật khẩu trong detail view

    form_overrides = {
        'user_type': SelectField,
        'gender': SelectField
    }

    form_choices = {
        'user_type': [(role.value, role.name.capitalize()) for role in UserRole],
    }

    def scaffold_form(self):
        form_class = super().scaffold_form()
        # Tạo trường password chỉ để nhập mới/chỉnh sửa
        form_class.password = PasswordField('Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        # Nếu nhập mật khẩu mới thì hash lại
        if form.password.data:
            model.password = generate_password_hash(form.password.data)
        super().on_model_change(form, model, is_created)

    def on_form_prefill(self, form, id):
        # Khi edit user, để trống password
        form.password.data = None

# ------------------- JobTypeAdmin -------------------
class JobTypeAdmin(AdminModelViewBase):
    pass

# ------------------- CompanyAdmin -------------------
class CompanyAdmin(AdminModelViewBase):
    column_list = (
        'company_name', 'company_tax_id', 'business_type', 'company_address',
        'established_date', 'status', 'phone_contact', 'legal_representative',
        'province_name', 'district_name', 'ward_name', 'user_name', '_actions'
    )

    form_columns = [
        'company_name', 'company_tax_id', 'business_type', 'company_address',
        'established_date', 'business_status', 'phone_contact', 'legal_representative',
        'province_code', 'district_code', 'ward_code', 'user_id'
    ]

    form_overrides = {
        'business_status': SelectField,
        'province_code': SelectField,
        'district_code': SelectField,
        'ward_code': SelectField,
        'user_id': SelectField,
    }

    form_args = {
        'business_status': {
            'choices': [(True, 'Hoạt động'), (False, 'Ngừng hoạt động')],
            'coerce': lambda x: x == 'True' or x is True,
        },
        'user_id': {
            'coerce': int,
        }
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

        form.user_id.choices = [
            (u.id, u.username)
            for u in User.query
            .filter(User.user_type == 'approver')
            .order_by(User.id)
            .all()
        ]

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

        form.user_id.choices = [
            (u.id, u.username)
            for u in User.query
            .filter(User.user_type == 'approver')
            .order_by(User.id)
            .all()
        ]

        return form

    def _populate_choices(self, form):
        # Province
        form.province_code.choices = [(p.code, p.full_name) for p in Province.query.order_by(Province.name).all()]
        # District
        if form.province_code.data:
            form.district_code.choices = [
                (d.code, d.full_name)
                for d in District.query.filter_by(province_code=form.province_code.data).order_by(District.name)
            ]
        else:
            form.district_code.choices = []
        # Ward
        if form.district_code.data:
            form.ward_code.choices = [
                (w.code, w.full_name)
                for w in Ward.query.filter_by(district_code=form.district_code.data).order_by(Ward.name)
            ]
        else:
            form.ward_code.choices = []

        form.user_id.choices = [(u.id, u.username) for u in User.query.order_by(User.id).all()]

    def on_model_change(self, form, model, is_created):
        form.populate_obj(model)

        if hasattr(form, 'business_status'):
            model.business_status = bool(form.business_status.data)

        super().on_model_change(form, model, is_created)

    edit_template = 'admin/company.html'
    create_template = 'admin/company.html'


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

# ------------------- TemplatesAdmin -------------------
class TemplatesAdmin(ModelView):
    column_list = ['id', 'name', 'background_preview', 'layout_preview', 'widget_preview', 'is_active', 'created_at', 'actions']
    column_filters = ['is_active', 'created_at']
    form_excluded_columns = ['created_at', 'updated_at', 'thumbnail']
    
    form_extra_fields = {
        'layout_json': TextAreaField('Layout JSON', 
                                   render_kw={'rows': 10, 'id': 'layout_json_field',
                                            'placeholder': 'Layout configuration will be auto-generated'}),
        'background': StringField('Background URL', 
                                 render_kw={'placeholder': 'https://example.com/background.jpg'}),
        'color_scheme': TextAreaField('Color Scheme (JSON)', 
                                     render_kw={'rows': 5, 'id': 'color_scheme_field',
                                              'placeholder': 'Color scheme will be auto-generated'}),
        'widget_config': TextAreaField('Widget Config (JSON)', 
                                      render_kw={'rows': 5, 'id': 'widget_config_field',
                                               'placeholder': 'Widget configuration will be auto-generated'}),
        'font_family': StringField('Font Family', default='Arial, sans-serif'),
        'font_size': StringField('Base Font Size', default='14px')
    }
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == UserRole.admin.value

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login-screen'))
    
    def on_form_prefill(self, form, id):
        """Điền dữ liệu có sẵn vào form khi chỉnh sửa"""
        template = Templates.query.get(id)
        if template:
            print(f"Loading template {id}: {template.name}")
            
            # Điền các trường cơ bản
            if hasattr(form, 'name'):
                form.name.data = template.name or ''
            
            if hasattr(form, 'background'):
                form.background.data = template.background or ''
            
            # Xử lý các trường JSON - đảm bảo format đúng
            json_fields = ['layout_json', 'widget_config', 'color_scheme']
            
            for field_name in json_fields:
                if hasattr(form, field_name):
                    field_value = getattr(template, field_name, None)
                    
                    if field_value and field_value.strip() and field_value not in ['[]', '{}']:
                        try:
                            # Parse và format lại JSON
                            if isinstance(field_value, str):
                                parsed_data = json.loads(field_value)
                            else:
                                parsed_data = field_value
                            
                            # Format với indent để dễ đọc
                            formatted_data = json.dumps(parsed_data, indent=2, ensure_ascii=False)
                            getattr(form, field_name).data = formatted_data
                            print(f"Formatted {field_name}: {formatted_data[:100]}...")
                            
                        except (json.JSONDecodeError, TypeError) as e:
                            print(f"Error parsing {field_name}: {e}")
                            # Giữ nguyên giá trị gốc nếu không parse được
                            getattr(form, field_name).data = field_value
                    else:
                        # Set giá trị mặc định cho trường rỗng
                        if field_name == 'layout_json':
                            getattr(form, field_name).data = '[]'
                        elif field_name == 'color_scheme':
                            default_colors = {
                                "primary": "#4a6cf7",
                                "secondary": "#6a79f7",
                                "background": "#ffffff",
                                "text": "#333333",
                                "accent": "#f3f4f6",
                                "header": "#1f2937",
                                "border": "#e5e7eb"
                            }
                            getattr(form, field_name).data = json.dumps(default_colors, indent=2)
                        else:  # widget_config
                            getattr(form, field_name).data = '{}'
    
    def on_model_change(self, form, model, is_created):
        """Xử lý khi tạo mới hoặc cập nhật template"""
        print(f"Saving template: {model.name}")
        
        if model.background and not model.thumbnail:
            model.thumbnail = model.background
        
        # Validate và xử lý JSON fields
        json_fields = {
            'layout_json': getattr(form, 'layout_json', None),
            'color_scheme': getattr(form, 'color_scheme', None),
            'widget_config': getattr(form, 'widget_config', None)
        }
        
        for field_name, field_obj in json_fields.items():
            if field_obj and hasattr(field_obj, 'data') and field_obj.data:
                field_data = field_obj.data.strip()
                if field_data:
                    try:
                        # Validate JSON
                        parsed_data = json.loads(field_data)
                        # Store as string
                        setattr(model, field_name, json.dumps(parsed_data, ensure_ascii=False))
                        print(f"Saved {field_name}: {getattr(model, field_name)}")
                    except json.JSONDecodeError as e:
                        raise ValueError(f"{field_name.replace('_', ' ').title()} must be valid JSON: {str(e)}")
                else:
                    # Set default for empty fields
                    if field_name == 'layout_json':
                        setattr(model, field_name, '[]')
                    elif field_name == 'color_scheme':
                        default_colors = {
                            "primary": "#4a6cf7",
                            "secondary": "#6a79f7",
                            "background": "#ffffff", 
                            "text": "#333333",
                            "accent": "#f3f4f6",
                            "header": "#1f2937",
                            "border": "#e5e7eb"
                        }
                        setattr(model, field_name, json.dumps(default_colors))
                    else:  # widget_config
                        setattr(model, field_name, '{}')
            else:
                # Handle None/empty cases
                if field_name == 'layout_json':
                    setattr(model, field_name, '[]')
                elif field_name == 'color_scheme':
                    default_colors = {
                        "primary": "#4a6cf7",
                        "secondary": "#6a79f7",
                        "background": "#ffffff",
                        "text": "#333333", 
                        "accent": "#f3f4f6",
                        "header": "#1f2937",
                        "border": "#e5e7eb"
                    }
                    setattr(model, field_name, json.dumps(default_colors))
                else:  # widget_config
                    setattr(model, field_name, '{}')
        
        # Set default values nếu chưa có
        if not model.font_family:
            model.font_family = 'Arial, sans-serif'
        
        if not model.font_size:
            model.font_size = '14px'
        
        print(f"Final model data:")
        print(f"  layout_json: {model.layout_json}")
        print(f"  widget_config: {model.widget_config}")
        print(f"  color_scheme: {model.color_scheme}")
        
        super().on_model_change(form, model, is_created)
    
    # Static methods for formatters
    @staticmethod
    def _background_preview(view, context, model, name):
        if model.background:
            return Markup(f'''
                <div style="position:relative; display:inline-block;">
                    <img src="{model.background}" style="width:100px;height:auto;border-radius:4px;border:1px solid #ddd;">
                    <a href="{model.background}" target="_blank" 
                       style="position:absolute;bottom:2px;right:2px;background:rgba(0,0,0,0.7);color:white;
                              padding:2px 6px;border-radius:3px;font-size:10px;text-decoration:none;">
                        View
                    </a>
                </div>
            ''')
        return Markup('<span class="text-muted">No background</span>')
    
    @staticmethod
    def _status_formatter(view, context, model, name):
        if model.is_active:
            return Markup('<span class="badge bg-success">Active</span>')
        return Markup('<span class="badge bg-secondary">Inactive</span>')
    
    @staticmethod
    def _json_preview(view, context, model, field_name):
        """Helper để hiển thị preview của JSON data"""
        field_value = getattr(model, field_name, None)
        if not field_value or field_value in ['[]', '{}']:
            return Markup('<span class="text-muted">Empty</span>')
        
        try:
            if isinstance(field_value, str):
                data = json.loads(field_value)
            else:
                data = field_value
            
            # Hiển thị số lượng items hoặc keys
            if isinstance(data, dict):
                count = len(data.keys())
                preview_text = f"{count} keys"
            elif isinstance(data, list):
                count = len(data)
                preview_text = f"{count} items"
            else:
                preview_text = "Data"
            
            return Markup(f'<span class="badge bg-info">{preview_text}</span>')
        except:
            return Markup('<span class="badge bg-warning">Invalid JSON</span>')
    
    @staticmethod
    def _layout_preview(view, context, model, name):
        return TemplatesAdmin._json_preview(view, context, model, 'layout_json')
    
    @staticmethod
    def _widget_preview(view, context, model, name):
        return TemplatesAdmin._json_preview(view, context, model, 'widget_config')
    
    @staticmethod
    def _actions_formatter(view, context, model, name):
        edit_url = get_url('.edit_view', id=model.id)
        delete_url = get_url('.delete_view', id=model.id)
        
        # Safe check for preview URL
        try:
            preview_url = url_for('cv.preview_template', template_id=model.id)
        except:
            preview_url = '#'
        
        return Markup(f'''
            <div class="btn-group" role="group">
                <a class="btn btn-sm btn-outline-primary" href="{edit_url}" title="Chỉnh sửa">
                    <i class="fas fa-edit"></i>
                </a>
                <a class="btn btn-sm btn-outline-info" href="{preview_url}" target="_blank" title="Xem trước">
                    <i class="fas fa-eye"></i>
                </a>
                <a class="btn btn-sm btn-outline-danger" href="{delete_url}" 
                   onclick="return confirm('Bạn có chắc muốn xóa template này?')" title="Xóa">
                    <i class="fas fa-trash"></i>
                </a>
            </div>
        ''')
    
    column_formatters = {
        'background_preview': _background_preview,
        'layout_preview': _layout_preview,
        'widget_preview': _widget_preview,
        'is_active': _status_formatter,
        'actions': _actions_formatter
    }
    
    column_labels = {
        'background_preview': 'Background',
        'layout_preview': 'Layout',
        'widget_preview': 'Widgets',
        'is_active': 'Status',
        'created_at': 'Created',
        'actions': 'Actions'
    }
    
    create_template = 'admin/template.html'
    edit_template = 'admin/template.html'
    
    def create_model(self, form):
        """Override để xử lý tạo mới template"""
        try:
            model = self.model()
            form.populate_obj(model)
            
            # Set default values cho template mới
            if not model.layout_json or model.layout_json.strip() == '':
                model.layout_json = '[]'
            if not model.widget_config or model.widget_config.strip() == '':
                model.widget_config = '{}'
            if not model.color_scheme or model.color_scheme.strip() == '':
                default_colors = {
                    "primary": "#4a6cf7",
                    "secondary": "#6a79f7",
                    "background": "#ffffff",
                    "text": "#333333",
                    "accent": "#f3f4f6", 
                    "header": "#1f2937",
                    "border": "#e5e7eb"
                }
                model.color_scheme = json.dumps(default_colors)
            if not model.font_family:
                model.font_family = 'Arial, sans-serif'
            if not model.font_size:
                model.font_size = '14px'
            if not hasattr(model, 'is_active') or model.is_active is None:
                model.is_active = True
            
            self.session.add(model)
            self.session.commit()
            return model
        except Exception as e:
            self.session.rollback()
            flash(f'Error creating template: {str(e)}', 'error')
            return False

    def update_model(self, form, model):
        """Override để xử lý cập nhật template"""
        try:
            form.populate_obj(model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            flash(f'Error updating template: {str(e)}', 'error')
            return False
        
    def _actions_formatter(view, context, model, name):
        edit_url = get_url('.edit_view', id=model.id)
        delete_url = get_url('.delete_view', id=model.id)
        builder_url = url_for('admin_template.admin_template_builder', template_id=model.id)
        
        return Markup(f'''
            <div class="btn-group" role="group">
                <a class="btn btn-sm btn-outline-primary" href="{edit_url}" title="Chỉnh sửa">
                    <i class="fas fa-edit"></i>
                </a>
                <a class="btn btn-sm btn-outline-success" href="{builder_url}" title="Template Builder">
                    <i class="fas fa-puzzle-piece"></i>
                </a>

                <a class="btn btn-sm btn-outline-danger" href="{delete_url}" 
                   onclick="return confirm('Bạn có chắc muốn xóa template này?')" title="Xóa">
                    <i class="fas fa-trash"></i>
                </a>
            </div>
        ''')
    
                #     <a class="btn btn-sm btn-outline-info" href="{preview_url}" target="_blank" title="Xem trước">
                #     <i class="fas fa-eye"></i>
                # </a>

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
