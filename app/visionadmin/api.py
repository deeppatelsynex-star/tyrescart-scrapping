"""
app/visionadmin/api.py - VisionAdmin CMS Controller & API Layer
Handles Page & Blog Management CRUD routes, file uploads, and JSON endpoints.
"""

import os
import time
import uuid
from flask import Blueprint, jsonify, render_template, request, session
from werkzeug.utils import secure_filename
from models.page import Page
from models.blog import Blog
from models.page_section import PageSection


def register_visionadmin_routes(app):
    """Registers all /visionadmin page, blog, and upload API endpoints."""

    # =========================================================================
    # 1. ADMIN UI ROUTES
    # =========================================================================

    @app.route('/visionadmin', methods=['GET'])
    @app.route('/visionadmin/', methods=['GET'])
    @app.route('/visionadmin/pages', methods=['GET'])
    @app.route('/visonadmin', methods=['GET'])
    @app.route('/visonadmin/', methods=['GET'])
    @app.route('/admin', methods=['GET'])
    @app.route('/admin/', methods=['GET'])
    @app.route('/admin/pages', methods=['GET'])
    def visionadmin_pages():
        return render_template('visionadmin/pages.html', page='pages')

    @app.route('/visionadmin/blogs', methods=['GET'])
    @app.route('/visonadmin/blogs', methods=['GET'])
    @app.route('/admin/blogs', methods=['GET'])
    def visionadmin_blogs():
        return render_template('visionadmin/blogs.html', page='blogs')

    @app.route('/visionadmin/sections', methods=['GET'])
    @app.route('/visionadmin/about-sections', methods=['GET'])
    @app.route('/visonadmin/sections', methods=['GET'])
    @app.route('/visonadmin/about-sections', methods=['GET'])
    @app.route('/admin/sections', methods=['GET'])
    @app.route('/admin/about-sections', methods=['GET'])
    def visionadmin_sections():
        return render_template('visionadmin/sections.html', page='sections')

    # =========================================================================
    # 2. FILE UPLOAD ENDPOINTS
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

    @app.route('/visionadmin/api/upload-blog-image', methods=['POST'])
    def visionadmin_upload_blog_image():
        file = request.files.get('file') or request.files.get('image')
        if not file or not file.filename:
            return jsonify({'error': 'No image file provided.'}), 400

        allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.avif'}
        orig_filename = secure_filename(file.filename)
        _, ext = os.path.splitext(orig_filename)
        ext = ext.lower()
        if ext not in allowed_extensions:
            return jsonify({'error': f'Invalid image format "{ext}". Allowed formats: PNG, JPG, JPEG, WEBP, SVG, GIF, AVIF'}), 400

        upload_folder = os.path.join(app.static_folder, 'uploads', 'blogs')
        os.makedirs(upload_folder, exist_ok=True)

        unique_name = f"blog_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"
        save_path = os.path.join(upload_folder, unique_name)
        file.save(save_path)

        web_url = f"/static/uploads/blogs/{unique_name}"
        return jsonify({
            'success': True,
            'url': web_url,
            'filename': unique_name,
            'message': 'Featured blog image uploaded successfully.'
        })

    # =========================================================================
    # 3. PAGES JSON API ENDPOINTS (/visionadmin/api/pages)
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
            return jsonify({'error': f'The slug "{slug}" is already in use. Please choose a different slug.'}), 409

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

        is_hard = request.args.get('hard') == '1' or request.args.get('permanent') == '1' or page.deleted_at is not None

        if is_hard:
            Page.hard_delete(page_id)
            return jsonify({
                'success': True,
                'message': f'Page "{page.get_title()}" permanently deleted from database.'
            })
        else:
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

    # =========================================================================
    # 4. BLOGS JSON API ENDPOINTS (/visionadmin/api/blogs)
    # =========================================================================

    @app.route('/visionadmin/api/categories', methods=['GET'])
    @app.route('/visionadmin/api/blog-categories', methods=['GET'])
    def visionadmin_get_categories():
        """Returns all distinct category names from existing blogs table."""
        categories = Blog.distinct_categories()
        return jsonify({'success': True, 'categories': categories})

    @app.route('/visionadmin/api/blogs', methods=['GET'])
    def visionadmin_get_blogs():
        locale = request.args.get('locale')
        include_deleted = request.args.get('trash') == '1'
        status_filter = request.args.get('status')
        query = (request.args.get('q') or '').strip()

        blogs = Blog.all(include_deleted=include_deleted)

        if include_deleted:
            blogs = [b for b in blogs if b.deleted_at is not None]
        else:
            blogs = [b for b in blogs if b.deleted_at is None]

        if status_filter in ('published', 'draft', 'archived'):
            blogs = [b for b in blogs if b.status == status_filter]

        if query:
            q_lower = query.lower()
            blogs = [
                b for b in blogs 
                if q_lower in b.get_title('en').lower() 
                or q_lower in b.get_title('ar').lower() 
                or q_lower in (b.slug or '').lower()
                or q_lower in b.get_short_desc('en').lower()
                or q_lower in (b.category_name or '').lower()
            ]

        all_active = [b for b in Blog.all(include_deleted=False) if b.deleted_at is None]
        metrics = {
            'total': len(all_active),
            'published': len([b for b in all_active if b.status == 'published']),
            'draft': len([b for b in all_active if b.status == 'draft']),
            'archived': len([b for b in all_active if b.status == 'archived']),
            'trash': len([b for b in Blog.all(include_deleted=True) if b.deleted_at is not None])
        }

        return jsonify({
            'success': True,
            'blogs': [b.to_dict(locale=locale) for b in blogs],
            'metrics': metrics,
            'count': len(blogs)
        })

    @app.route('/visionadmin/api/blogs/<int:blog_id>', methods=['GET'])
    def visionadmin_get_blog(blog_id):
        blog = Blog.find_by_id(blog_id)
        if not blog:
            return jsonify({'error': 'Blog article not found.'}), 404
        return jsonify({'success': True, 'blog': blog.to_dict()})

    @app.route('/visionadmin/api/blogs', methods=['POST'])
    def visionadmin_create_blog():
        data = request.get_json(silent=True) or {}

        title = data.get('title') or {}
        en_title = (title.get('en') if isinstance(title, dict) else str(title)).strip()
        if not en_title:
            return jsonify({'error': 'English Blog Title is required.'}), 400

        slug = (data.get('slug') or '').strip()
        if not slug:
            slug = Blog.slugify(en_title)
        else:
            slug = Blog.slugify(slug)

        if not Blog.is_slug_available(slug):
            return jsonify({'error': f'The slug "{slug}" is already in use. Please choose a unique slug.'}), 409

        try:
            blog = Blog.create(
                title=title if isinstance(title, dict) else {"en": en_title, "ar": ""},
                slug=slug,
                content=data.get('content') or {"en": "", "ar": ""},
                short_description=data.get('short_description') or {"en": "", "ar": ""},
                image=data.get('image'),
                category_name=(data.get('category_name') or data.get('category') or '').strip() or None,
                blog_category_id=data.get('blog_category_id'),
                author_id=data.get('author_id') or session.get('user_id') or 1,
                status=data.get('status') or 'draft',
                published_at=data.get('published_at'),
                meta_title=data.get('meta_title'),
                meta_desc=data.get('meta_desc'),
                created_by=session.get('user_id'),
                updated_by=session.get('user_id')
            )
            return jsonify({
                'success': True,
                'blog': blog.to_dict(),
                'message': f'Blog "{blog.get_title()}" created successfully.'
            }), 201
        except Exception as e:
            if 'Duplicate entry' in str(e) or 'IntegrityError' in type(e).__name__:
                return jsonify({'error': f'The slug "{slug}" is already in use.'}), 409
            return jsonify({'error': f'Failed to create blog: {str(e)}'}), 500

    @app.route('/visionadmin/api/blogs/<int:blog_id>', methods=['PUT'])
    def visionadmin_update_blog(blog_id):
        blog = Blog.find_by_id(blog_id)
        if not blog:
            return jsonify({'error': 'Blog article not found.'}), 404

        data = request.get_json(silent=True) or {}

        if 'slug' in data and data['slug']:
            new_slug = Blog.slugify(data['slug'])
            if not Blog.is_slug_available(new_slug, exclude_id=blog_id):
                return jsonify({'error': f'The slug "{new_slug}" is already in use.'}), 409
            data['slug'] = new_slug

        data['updated_by'] = session.get('user_id')

        try:
            blog.update(**data)
            refreshed = Blog.find_by_id(blog_id)
            return jsonify({
                'success': True,
                'blog': refreshed.to_dict(),
                'message': f'Blog "{refreshed.get_title()}" updated successfully.'
            })
        except Exception as e:
            if 'Duplicate entry' in str(e) or 'IntegrityError' in type(e).__name__:
                return jsonify({'error': 'The specified slug is already in use.'}), 409
            return jsonify({'error': f'Failed to update blog: {str(e)}'}), 500

    @app.route('/visionadmin/api/blogs/<int:blog_id>', methods=['DELETE'])
    def visionadmin_delete_blog(blog_id):
        blog = Blog.find_by_id(blog_id)
        if not blog:
            return jsonify({'error': 'Blog article not found.'}), 404

        is_hard = request.args.get('hard') == '1' or request.args.get('permanent') == '1' or blog.deleted_at is not None

        if is_hard:
            Blog.hard_delete(blog_id)
            return jsonify({
                'success': True,
                'message': f'Article "{blog.get_title()}" permanently deleted from database.'
            })
        else:
            Blog.soft_delete(blog_id)
            return jsonify({
                'success': True,
                'message': f'Article "{blog.get_title()}" moved to trash.'
            })

    @app.route('/visionadmin/api/blogs/<int:blog_id>/restore', methods=['POST'])
    def visionadmin_restore_blog(blog_id):
        Blog.restore(blog_id)
        return jsonify({
            'success': True,
            'message': 'Blog article restored successfully.'
        })

    # =========================================================================
    # 5. PAGE SECTIONS CRUD & REORDER API (About Us, etc.)
    # =========================================================================

    @app.route('/visionadmin/api/sections', methods=['GET'])
    def visionadmin_get_sections():
        """Returns all sections for a page (including inactive) ordered by sort_order."""
        page_slug = request.args.get('page') or request.args.get('page_slug') or 'about-us'
        sections = PageSection.all_for_page(page_slug=page_slug, include_inactive=True)
        return jsonify({
            'page': page_slug,
            'sections': sections,
            'count': len(sections)
        })

    @app.route('/visionadmin/api/sections/<int:section_id>', methods=['GET'])
    def visionadmin_get_section_detail(section_id):
        """Returns a single section by id."""
        sec = PageSection.find_by_id(section_id)
        if not sec:
            return jsonify({'error': 'Section not found.'}), 404
        return jsonify({'section': sec})

    @app.route('/visionadmin/api/sections', methods=['POST'])
    def visionadmin_create_section():
        """Creates a new section."""
        data = request.get_json(silent=True) or request.form.to_dict()
        if not data:
            return jsonify({'error': 'No data provided.'}), 400

        section_type = data.get('section_type')
        if not section_type:
            return jsonify({'error': 'section_type is required.'}), 400

        try:
            new_sec = PageSection.create(data)
            return jsonify({
                'success': True,
                'section': new_sec,
                'message': 'Section added successfully.'
            }), 201
        except Exception as e:
            return jsonify({'error': f'Failed to create section: {str(e)}'}), 500

    @app.route('/visionadmin/api/sections/<int:section_id>', methods=['PUT'])
    def visionadmin_update_section(section_id):
        """Updates an existing section."""
        sec = PageSection.find_by_id(section_id)
        if not sec:
            return jsonify({'error': 'Section not found.'}), 404

        data = request.get_json(silent=True) or request.form.to_dict()
        if not data:
            return jsonify({'error': 'No data provided.'}), 400

        try:
            updated = PageSection.update(section_id, data)
            return jsonify({
                'success': True,
                'section': updated,
                'message': 'Section updated successfully.'
            })
        except Exception as e:
            return jsonify({'error': f'Failed to update section: {str(e)}'}), 500

    @app.route('/visionadmin/api/sections/<int:section_id>', methods=['DELETE'])
    def visionadmin_delete_section(section_id):
        """Soft deletes a section."""
        sec = PageSection.find_by_id(section_id)
        if not sec:
            return jsonify({'error': 'Section not found.'}), 404

        PageSection.soft_delete(section_id)
        return jsonify({
            'success': True,
            'message': 'Section deleted successfully.'
        })

    @app.route('/visionadmin/api/sections/<int:section_id>/toggle', methods=['POST'])
    def visionadmin_toggle_section(section_id):
        """Toggles active/disabled state of a section."""
        sec = PageSection.find_by_id(section_id)
        if not sec:
            return jsonify({'error': 'Section not found.'}), 404

        toggled = PageSection.toggle_active(section_id)
        status_str = 'enabled' if toggled.get('is_active') else 'disabled'
        return jsonify({
            'success': True,
            'section': toggled,
            'message': f'Section {status_str} successfully.'
        })

    @app.route('/visionadmin/api/sections/reorder', methods=['POST'])
    def visionadmin_reorder_sections():
        """Updates section order based on ordered list of IDs."""
        data = request.get_json(silent=True) or {}
        ordered_ids = data.get('ordered_ids') or data.get('ids') or []
        if not ordered_ids or not isinstance(ordered_ids, list):
            return jsonify({'error': 'ordered_ids list is required.'}), 400

        try:
            PageSection.reorder(ordered_ids)
            return jsonify({
                'success': True,
                'message': 'Section order saved successfully.'
            })
        except Exception as e:
            return jsonify({'error': f'Failed to reorder sections: {str(e)}'}), 500

    # =========================================================================
    # 6. PUBLIC API ENDPOINTS (Returns active sections ordered by sort_order)
    # =========================================================================

    @app.route('/api/pages/<slug>/sections', methods=['GET'])
    @app.route('/api/sections/<slug>', methods=['GET'])
    @app.route('/api/pages/about-us/sections', methods=['GET'])
    def public_get_page_sections(slug='about-us'):
        """Public API returning active sections for a page ordered by sort_order."""
        target_slug = slug if slug else 'about-us'
        locale = request.args.get('locale') or request.args.get('lang')
        sections = PageSection.all_for_page(page_slug=target_slug, include_inactive=False)
        
        if locale:
            formatted = [PageSection.to_localized_dict(s, locale=locale) for s in sections]
        else:
            formatted = sections

        return jsonify({
            'page': target_slug,
            'sections': formatted,
            'count': len(formatted)
        })
