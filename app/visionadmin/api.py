"""
app/visionadmin/api.py - VisionAdmin CMS Controller & API Layer
Handles Page Management CRUD routes, banner file uploads, and JSON endpoints.
"""

import os
import time
import uuid
from flask import Blueprint, jsonify, render_template, request, session
from werkzeug.utils import secure_filename
from models.page import Page


def register_visionadmin_routes(app):
    """Registers all /visionadmin page and API endpoints."""

    # =========================================================================
    # 1. PAGE ROUTES
    # =========================================================================

    @app.route('/visionadmin', methods=['GET'])
    @app.route('/visionadmin/', methods=['GET'])
    @app.route('/visionadmin/pages', methods=['GET'])
    def visionadmin_pages():
        return render_template('visionadmin/pages.html', page='pages')

    # =========================================================================
    # 2. BANNER IMAGE UPLOAD ENDPOINT
    # =========================================================================

    @app.route('/visionadmin/api/upload-banner', methods=['POST'])
    def visionadmin_upload_banner():
        file = request.files.get('file') or request.files.get('banner')
        if not file or not file.filename:
            return jsonify({'error': 'No image file provided.'}), 400

        allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.avif'}
        orig_filename = secure_filename(file.filename)
        _, ext = os.path.splitext(orig_filename)
        ext = ext.lower()
        if ext not in allowed_extensions:
            return jsonify({'error': f'Invalid image format "{ext}". Allowed formats: PNG, JPG, JPEG, WEBP, SVG, GIF, AVIF'}), 400

        upload_folder = os.path.join(app.static_folder, 'uploads', 'pages')
        os.makedirs(upload_folder, exist_ok=True)

        unique_name = f"banner_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"
        save_path = os.path.join(upload_folder, unique_name)
        file.save(save_path)

        web_url = f"/static/uploads/pages/{unique_name}"
        return jsonify({
            'success': True,
            'url': web_url,
            'filename': unique_name,
            'message': 'Banner image uploaded successfully.'
        })

    # =========================================================================
    # 3. JSON API ENDPOINTS (/visionadmin/api/pages)
    # =========================================================================

    @app.route('/visionadmin/api/pages', methods=['GET'])
    def visionadmin_get_pages():
        locale = request.args.get('locale')
        include_deleted = request.args.get('trash') == '1'
        status_filter = request.args.get('status')
        query = (request.args.get('q') or '').strip()

        pages = Page.all(include_deleted=include_deleted)

        if include_deleted:
            pages = [p for p in pages if p.deleted_at is not None]
        else:
            pages = [p for p in pages if p.deleted_at is None]

        if status_filter == 'active':
            pages = [p for p in pages if p.is_active]
        elif status_filter == 'inactive':
            pages = [p for p in pages if not p.is_active]

        if query:
            q_lower = query.lower()
            pages = [
                p for p in pages 
                if q_lower in p.get_title('en').lower() 
                or q_lower in p.get_title('ar').lower() 
                or q_lower in (p.slug or '').lower()
            ]

        all_active = [p for p in Page.all(include_deleted=False) if p.deleted_at is None]
        metrics = {
            'total': len(all_active),
            'active': len([p for p in all_active if p.is_active]),
            'inactive': len([p for p in all_active if not p.is_active]),
            'trash': len([p for p in Page.all(include_deleted=True) if p.deleted_at is not None])
        }

        return jsonify({
            'success': True,
            'pages': [p.to_dict(locale=locale) for p in pages],
            'metrics': metrics,
            'count': len(pages)
        })

    @app.route('/visionadmin/api/pages/<int:page_id>', methods=['GET'])
    def visionadmin_get_page(page_id):
        page = Page.find_by_id(page_id)
        if not page:
            return jsonify({'error': 'Page not found.'}), 404
        return jsonify({'success': True, 'page': page.to_dict()})

    @app.route('/visionadmin/api/pages', methods=['POST'])
    def visionadmin_create_page():
        data = request.get_json(silent=True) or {}
        
        # Validation
        title = data.get('title') or {}
        en_title = (title.get('en') if isinstance(title, dict) else str(title)).strip()
        if not en_title:
            return jsonify({'error': 'English Page Title is required.'}), 400

        slug = (data.get('slug') or '').strip()
        if not slug:
            slug = Page.slugify(en_title)
        else:
            slug = Page.slugify(slug)

        if not Page.is_slug_available(slug):
            return jsonify({'error': f'The slug "{slug}" is already in use by another page. Please choose a different slug.'}), 409

        try:
            page = Page.create(
                title=title if isinstance(title, dict) else {"en": en_title, "ar": ""},
                slug=slug,
                content=data.get('content') or {"en": "", "ar": ""},
                banner_image=data.get('banner_image'),
                seo_title=data.get('seo_title'),
                meta_description=data.get('meta_description'),
                is_active=bool(data.get('is_active', True)),
                created_by=session.get('user_id'),
                updated_by=session.get('user_id')
            )
            return jsonify({
                'success': True,
                'page': page.to_dict(),
                'message': f'Page "{page.get_title()}" created successfully.'
            }), 201
        except Exception as e:
            if 'Duplicate entry' in str(e) or 'IntegrityError' in type(e).__name__:
                return jsonify({'error': f'The slug "{slug}" is already in use. Please enter a different slug.'}), 409
            return jsonify({'error': f'Failed to create page: {str(e)}'}), 500

    @app.route('/visionadmin/api/pages/<int:page_id>', methods=['PUT'])
    def visionadmin_update_page(page_id):
        page = Page.find_by_id(page_id)
        if not page:
            return jsonify({'error': 'Page not found.'}), 404

        data = request.get_json(silent=True) or {}
        
        if 'slug' in data and data['slug']:
            new_slug = Page.slugify(data['slug'])
            if not Page.is_slug_available(new_slug, exclude_id=page_id):
                return jsonify({'error': f'The slug "{new_slug}" is already in use.'}), 409
            data['slug'] = new_slug

        data['updated_by'] = session.get('user_id')

        try:
            page.update(**data)
            refreshed = Page.find_by_id(page_id)
            return jsonify({
                'success': True,
                'page': refreshed.to_dict(),
                'message': f'Page "{refreshed.get_title()}" updated successfully.'
            })
        except Exception as e:
            if 'Duplicate entry' in str(e) or 'IntegrityError' in type(e).__name__:
                return jsonify({'error': 'The specified slug is already in use.'}), 409
            return jsonify({'error': f'Failed to update page: {str(e)}'}), 500

    @app.route('/visionadmin/api/pages/<int:page_id>', methods=['DELETE'])
    def visionadmin_delete_page(page_id):
        page = Page.find_by_id(page_id)
        if not page:
            return jsonify({'error': 'Page not found.'}), 404

        Page.soft_delete(page_id)
        return jsonify({
            'success': True,
            'message': f'Page "{page.get_title()}" moved to trash.'
        })

    @app.route('/visionadmin/api/pages/<int:page_id>/restore', methods=['POST'])
    def visionadmin_restore_page(page_id):
        Page.restore(page_id)
        return jsonify({
            'success': True,
            'message': 'Page restored successfully.'
        })
