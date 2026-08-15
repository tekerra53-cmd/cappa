import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.admin.services import create_user
from app.models.user import User

app = create_app()
with app.app_context():
    username = 'ui.test.lecturer'
    email = 'ui.test.lecturer@example.com'
    if User.query.filter_by(username=username).first():
        print('User already exists:', username)
    else:
        try:
            u = create_user(username, email, 'TestPass123', 'lecturer')
            print('Created:', u.username, u.email, u.role)
        except Exception as e:
            print('Create error:', e)
    lec = User.query.filter_by(role='lecturer').order_by(User.username).all()
    print('Lecturers count:', len(lec))
    print([u.username for u in lec])
