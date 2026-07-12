from flask import Flask, redirect, url_for
from .config import Config
from .extensions import db, migrate, login_manager, csrf


def _init_database(app):
    with app.app_context():
        db.create_all()

        from .models.user import User

        if not User.query.filter_by(role='admin').first():
            admin = User()
            admin.username = 'admin'
            admin.email = 'admin@srms.local'
            admin.role = 'admin'
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

        from seed import _ensure_demo_accounts
        _ensure_demo_accounts(app)


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)

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

    return app
