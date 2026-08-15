import re
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
        db.drop_all()
        db.create_all()
        admin = User(username='testadmin', email='testadmin@test.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        lecturer = User(username='test.lecturer', email='lecturer@test.com', role='lecturer')
        db.session.add(lecturer)
        db.session.commit()
        
        # Store lecturer id for test
        app.config['TEST_LECTURER_ID'] = lecturer.id
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_advisor_assignment(client, app):
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        assert admin is not None, "Admin not found"
        
        lecturer_id = app.config['TEST_LECTURER_ID']
        
        # Login
        resp = client.get('/login')
        html = resp.data.decode()
        
        csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
        assert csrf_match is not None, "CSRF token not found on login page"
        csrf_token = csrf_match.group(1)
        
        login_resp = client.post('/login', data={
            'username': 'testadmin',
            'password': 'admin123',
            'csrf_token': csrf_token
        })
        assert login_resp.status_code == 302, f"Login failed: {login_resp.status_code}"
        
        # Get users page
        resp = client.get('/admin/users')
        assert resp.status_code == 200
        html = resp.data.decode()
        csrf_match2 = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
        assert csrf_match2 is not None, "CSRF token not found on users page"
        csrf_token2 = csrf_match2.group(1)
        
        # Submit advisor form
        response = client.post('/admin/advisors/assign', data={
            'lecturer_id': str(lecturer_id),
            'level': '300',
            'csrf_token': csrf_token2
        })
        print(f"Status: {response.status_code}")
        print(f"Location: {response.headers.get('Location', 'N/A')}")
        
        # Follow redirect
        resp2 = client.get(response.headers.get('Location', '/admin/users'))
        html2 = resp2.data.decode()
        
        if 'Not a valid choice' in html2:
            print("FOUND THE ERROR: Not a valid choice")
            select_match = re.search(r'<select[^>]*name="lecturer_id"[^>]*>.*?</select>', html2, re.DOTALL)
            if select_match:
                print(f"Select element: {select_match.group(0)[:500]}")
        else:
            print("No error found")
            flash_pattern = re.findall(r'<div class="alert[^"]*"[^>]*>(.*?)</div>', html2, re.DOTALL)
            for f in flash_pattern:
                print(f'Flash: {f.strip()[:100]}')
