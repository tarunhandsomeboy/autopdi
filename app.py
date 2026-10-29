import os
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify, session, request
from flask_cors import CORS
from config import config_by_name, BASE_DIR
from models import db
from models.user import User
from models.notification import Notification

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.customer_routes import customer_bp
from routes.inspector_routes import inspector_bp
from routes.booking_routes import booking_bp
from routes.inspection_routes import inspection_bp
from routes.report_routes import report_bp
from routes.admin_routes import admin_bp
from routes.issue_routes import issue_bp


def create_app(config_name: str = None) -> Flask:
    """Application Factory Pattern."""
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Enable CORS
    CORS(app)

    # Initialize Database
    db.init_app(app)

    # Ensure Upload Directories Exist
    os.makedirs(app.config['INSPECTIONS_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROFILES_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOCUMENTS_UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(inspector_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(inspection_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(issue_bp)

    # Global Context Processor
    @app.context_processor
    def inject_global_data():
        current_user = None
        unread_notifications_count = 0
        if 'user_id' in session:
            current_user = User.query.get(session['user_id'])
            if current_user:
                unread_notifications_count = Notification.query.filter_by(
                    user_id=current_user.id, is_read=False
                ).count()
        return dict(
            current_user=current_user,
            unread_notifications_count=unread_notifications_count,
            current_year=2026
        )

    # Landing Page Route
    @app.route('/')     
    def index():
        return render_template('index.html')

    # Static File Uploads Route
    @app.route('/uploads/<path:folder>/<path:filename>')
    def serve_upload(folder, filename):
        target_dir = app.config['UPLOAD_FOLDER'] / folder
        return send_from_directory(target_dir, filename)

    # Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "message": "Bad Request: " + str(error)}), 400
        return render_template('base.html', error_title="400 - Bad Request", error_msg="The request could not be processed."), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "message": "Unauthorized access."}), 401
        return render_template('base.html', error_title="401 - Unauthorized", error_msg="Please log in to access this page."), 401

    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "message": "Access forbidden: Insufficient permissions."}), 403
        return render_template('base.html', error_title="403 - Forbidden", error_msg="You do not have permission to view this resource."), 403

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "message": "Resource not found."}), 404
        return render_template('base.html', error_title="404 - Not Found", error_msg="The requested page or resource could not be found."), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({"success": False, "message": "Internal Server Error."}), 500
        return render_template('base.html', error_title="500 - Server Error", error_msg="An unexpected error occurred. Please try again."), 500

    return app


if __name__ == '__main__':
    app = create_app('development')
    port = int(os.getenv('PORT', 5000))
    print(f"[START] AUTO PDI Server starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
