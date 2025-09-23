
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Templates, UserRole
import json
from datetime import datetime

admin_template_bp = Blueprint('admin_template', __name__, url_prefix='/admin/template')


@admin_template_bp.route('/<int:template_id>')
@login_required
def api_get_template(template_id):
    """API to get template data"""
    try:
        template = Templates.query.get_or_404(template_id)
        
        # Ensure JSON fields are properly formatted
        layout_json = template.layout_json if template.layout_json else '[]'
        widget_config = template.widget_config if template.widget_config else '{}'
        color_scheme = template.color_scheme if template.color_scheme else '{}'

        return jsonify({
            'id': template.id,
            'name': template.name,
            'background': template.background or '',
            'layout_json': json.loads(layout_json),
            'widget_config': json.loads(widget_config),
            'color_scheme': json.loads(color_scheme),
            'font_family': template.font_family or 'Arial, sans-serif',
            'font_size': template.font_size or '14px'
        })
    except Exception as e:
        print(f"Error loading template: {e}")
        return jsonify({'error': str(e)}), 500

@admin_template_bp.route('/save', methods=['POST','PUT'])
@login_required
def api_save_template():
    """API to save template data"""
    try:
        # Check if request is JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        print('Received data:', data)  # Log dữ liệu nhận được

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Template name is required'}), 400
        
        # Create or update template
        template_id = data.get('id')
        if template_id:
            template = Templates.query.get(template_id)
            if not template:
                return jsonify({'error': 'Template not found'}), 404
        else:
            template = Templates()
            db.session.add(template)
        
        # Update template fields
        template.name = data['name']
        template.background = data.get('background', '')
        template.layout_json = json.dumps(data.get('layout_json', []))
        template.widget_config = json.dumps(data.get('widget_config', {}))
        template.color_scheme = json.dumps(data.get('color_scheme', {}))
        template.font_family = data.get('font_family', 'Arial, sans-serif')
        template.font_size = data.get('font_size', '14px')
        template.updated_at = datetime.utcnow()

        db.session.commit()
        return jsonify({'success': True, 'message': 'Template saved successfully', 'template_id': template.id})
    except Exception as e:
        db.session.rollback()
        print('Error saving template:', str(e))  # Log lỗi
        return jsonify({'error': str(e)}), 500