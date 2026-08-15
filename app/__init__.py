import os
import logging

from flask import Flask, redirect, url_for, jsonify
from .config import Config
from .extensions import db, migrate, login_manager, csrf

logger = logging.getLogger(__name__)


def _init_database(app):
    if app.config.get('TESTING', False) or os.environ.get('PYTEST_CURRENT_TEST'):
        return

    with app.app_context():
        try:
            db.create_all()
            logger.info('Database tables created/verified')
        except Exception as e:
            logger.error(f'Database create_all failed: {e}')
            return

        try:
            from .models.user import User

            if not User.query.filter_by(role='admin').first():
                admin = User()
                admin.username = 'admin'
                admin.email = 'admin@srms.local'
                admin.role = 'admin'
                admin.set_password('123456')
                db.session.add(admin)
                db.session.commit()
                logger.info('Default admin user created')
        except Exception as e:
            logger.error(f'Admin user creation failed: {e}')
            db.session.rollback()
            return

        if os.environ.get('VERCEL'):
            logger.info('Vercel environment detected, skipping demo seeding')
            return

        try:
            from seed import _ensure_demo_accounts
            _ensure_demo_accounts(app)
            logger.info('Demo accounts seeded')
        except Exception as e:
            logger.error(f'Demo seeding failed: {e}')


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)

    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'not set')
    logger.info(f'Starting app with DATABASE_URI: {db_uri}')

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # type: ignore[assignment]

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .lecturer.routes import lecturer_bp
    from .student.routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(lecturer_bp, url_prefix='/lecturer')
    app.register_blueprint(student_bp, url_prefix='/student')

    @app.route('/health')
    def health():
        try:
            db.session.execute(db.text('SELECT 1'))
            return jsonify({'status': 'healthy', 'database': 'connected'})
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'database': str(e)}), 500

    # Initialize database and demo data. Skip demo seeding when testing to
    # avoid interfering with unit tests that expect a clean database.
    if not app.config.get('TESTING', False):
        _init_database(app)

    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            if current_user.role == 'lecturer':
                return redirect(url_for('lecturer.dashboard'))
            if current_user.role == 'student':
                return redirect(url_for('student.dashboard'))
        return redirect(url_for('auth.login'))

    logger.info('App initialization complete')
    return app
