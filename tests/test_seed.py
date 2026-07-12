import os


def test_seed_database_populates_demo_accounts_and_results(tmp_path, monkeypatch):
    db_path = tmp_path / 'demo_seed.sqlite'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db_path}')
    monkeypatch.setenv('SECRET_KEY', 'test-secret')

    if db_path.exists():
        db_path.unlink()

    from seed import seed_database

    seed_database()

    from app import create_app
    from app.extensions import db
    from app.models import User, Student, Result

    app = create_app()
    with app.app_context():
        assert User.query.filter_by(role='lecturer').count() >= 5
        assert Student.query.count() >= 40
        assert Result.query.count() >= 200

        db.session.remove()
