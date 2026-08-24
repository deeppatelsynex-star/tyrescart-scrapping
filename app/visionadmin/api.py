"""
app/visionadmin/api.py - VisionAdmin CMS Controller & API Layer
Handles Page Management CRUD routes and JSON endpoints for static pages.
"""

from flask import Blueprint, jsonify, render_template, request, session
from auth import login_required_api, login_required_page, require_csrf
from models.page import Page


def register_visionadmin_routes(app):
    """Registers all /visionadmin page and API endpoints."""

    # =========================================================================
    # 1. PAGE ROUTES
    # =========================================================================

    @app.route('/visionadmin', methods=['GET'])
    @app.route('/visionadmin/', methods=['GET'])
    @app.route('/visionadmin/pages', methods=['GET'])
    @login_required_page
    def visionadmin_pages():
        return render_template('visionadmin/pages.html', page='pages')

    # =========================================================================
    # 2. JSON API ENDPOINTS (/visionadmin/api/pages)
    # =========================================================================

    @app.route('/visionadmin/api/pages', methods=['GET'])
    @login_required_api
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

        if status_filter and status_filter != 'all':
            pages = [p for p in pages if p.status == status_filter]

        if query:
            q_lower = query.lower()
            pages = [
                p for p in pages 
                if q_lower in p.get_title('en').lower() 
                or q_lower in p.get_title('ar').lower() 
                or q_lower in (p.slug or '').lower()
            ]

        # Calculate metrics
        all_active = [p for p in Page.all(include_deleted=False) if p.deleted_at is None]
        metrics = {
            'total': len(all_active),
            'published': len([p for p in all_active if p.status == 'published']),
            'draft': len([p for p in all_active if p.status == 'draft']),
            'in_header': len([p for p in all_active if p.show_in_header]),
            'in_footer': len([p for p in all_active if p.show_in_footer]),
            'trash': len([p for p in Page.all(include_deleted=True) if p.deleted_at is not None])
        }

        return jsonify({
            'success': True,
            'pages': [p.to_dict(locale=locale) for p in pages],
            'metrics': metrics,
            'count': len(pages)
        })

    @app.route('/visionadmin/api/pages/<int:page_id>', methods=['GET'])
    @login_required_api
    def visionadmin_get_page(page_id):
        page = Page.find_by_id(page_id)
        if not page:
            return jsonify({'error': 'Page not found.'}), 404
        return jsonify({'success': True, 'page': page.to_dict()})

    @app.route('/visionadmin/api/pages', methods=['POST'])
    @login_required_api
    @require_csrf
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
            return jsonify({'error': f'The slug "{slug}" is already in use.'}), 409

        page = Page.create(
            title=title if isinstance(title, dict) else {"en": en_title, "ar": ""},
            slug=slug,
            content=data.get('content') or {"en": "", "ar": ""},
            excerpt=data.get('excerpt') or {"en": "", "ar": ""},
            template=data.get('template', 'default'),
            featured_image=data.get('featured_image'),
            status=data.get('status', 'draft'),
            published_at=data.get('published_at'),
            show_in_footer=bool(data.get('show_in_footer')),
            show_in_header=bool(data.get('show_in_header')),
            sort_order=int(data.get('sort_order') or 0),
            meta_title=data.get('meta_title'),
            meta_desc=data.get('meta_desc'),
            canonical_url=data.get('canonical_url'),
            created_by=session.get('user_id')
        )
        return jsonify({
            'success': True,
            'page': page.to_dict(),
            'message': f'Page "{page.get_title()}" created successfully.'
        }), 201

    @app.route('/visionadmin/api/pages/<int:page_id>', methods=['PUT'])
    @login_required_api
    @require_csrf
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

        page.update(**data)
        refreshed = Page.find_by_id(page_id)
        return jsonify({
            'success': True,
            'page': refreshed.to_dict(),
            'message': f'Page "{refreshed.get_title()}" updated successfully.'
        })

    @app.route('/visionadmin/api/pages/<int:page_id>', methods=['DELETE'])
    @login_required_api
    @require_csrf
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
    @login_required_api
    @require_csrf
    def visionadmin_restore_page(page_id):
        Page.restore(page_id)
        return jsonify({
            'success': True,
            'message': 'Page restored successfully.'
        })
