"""
app/visionadmin/Visionadminroute.py - VisionAdmin CMS page routes.

Serves the VisionAdmin HTML pages only (Pages/Blogs/Sections manager UIs).
The JSON API endpoints that back these pages (/visionadmin/api/*) live in
the unified app/api.py alongside the tcsadmin and public client APIs.
"""

from flask import render_template


def register_visionadmin_routes(app):
    """Registers the /visionadmin (and /admin, /visonadmin aliases) page routes."""

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

    @app.route('/visionadmin/settings', methods=['GET'])
    @app.route('/visionadmin/config', methods=['GET'])
    @app.route('/visionadmin/reviewer-settings', methods=['GET'])
    @app.route('/visonadmin/settings', methods=['GET'])
    @app.route('/visonadmin/config', methods=['GET'])
    @app.route('/admin/settings', methods=['GET'])
    @app.route('/admin/config', methods=['GET'])
    def visionadmin_settings():
        return render_template('visionadmin/settings.html', page='settings')

