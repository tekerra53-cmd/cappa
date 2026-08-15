import pytest
from app import create_app
from app.models.user import User
from app.extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        from app.auth.routes import init_admin
        from flask import request
        with app.test_request_context('/init'):
            init_admin()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_admin_login(client):
    import re
    response = client.get('/login')
    html = response.data.decode()
    csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    assert csrf_match is not None, "CSRF token not found on login page"
    csrf_token = csrf_match.group(1)
    
    response = client.post('/login', data={
        'username': 'admin',
        'password': '123456',
        'csrf_token': csrf_token
    })
    assert response.status_code == 302, f"Login failed: {response.status_code}"
    assert response.headers['Location'].endswith('/')
