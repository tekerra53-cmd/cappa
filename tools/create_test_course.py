import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.admin.services import create_course
from app.models.user import User
from app.models.course import Course

app = create_app()
with app.app_context():
    lecturer = User.query.filter_by(username='ui.test.lecturer').first()
    if not lecturer:
        print('Lecturer not found')
    else:
        try:
            c = create_course('TST101', 'Test Course', 3, '1', '100', lecturer.id)
            print('Created course', c.code)
        except Exception as e:
            print('Create course error:', e)
    courses = Course.query.order_by(Course.code).all()
    print('Courses count:', len(courses))
    print([(c.code, c.title, c.lecturer.username if c.lecturer else None) for c in courses])
