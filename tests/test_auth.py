import pytest
from app import create_app
from app.models import User
from app.extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_admin_creation(app):
    with app.app_context():
        from app.auth.routes import init_admin
        with app.test_request_context('/init'):
            init_admin()
        admin = User.query.filter_by(role='admin').first()
        assert admin is not None
        assert admin.username == 'admin'


def test_user_creation(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com', role='student')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        retrieved = User.query.filter_by(username='testuser').first()
        assert retrieved is not None
        assert retrieved.check_password('password')
        assert not retrieved.check_password('wrong')