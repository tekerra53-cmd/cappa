import os
from pathlib import Path
from app import create_app
from app.extensions import db
from app.models import Course, Student, AcademicSession
import seed

# use a fresh temporary db for inspection
path = Path('tmp_inspect.sqlite')
if path.exists():
    path.unlink()
os.environ['DATABASE_URL'] = f'sqlite:///{path.absolute()}'
app = create_app()
with app.app_context():
    db.create_all()
    # create minimal admins/lecturers/sessions/courses
    from app.models import User, AcademicSession, Course
    admin = User(username='admin', email='admin@gmail.com', role='admin')
    admin.set_password('123456')
    db.session.add(admin)
    lecturers = []
    for index, (name, email) in enumerate(zip(seed.LECTURER_NAMES, seed.LECTURER_EMAILS), start=1):
        lecturer = User(username=name.lower().replace('dr. ', '').replace('prof. ', '').replace(' ', '.'), email=email, role='lecturer')
        lecturer.set_password('123456')
        db.session.add(lecturer)
        lecturers.append(lecturer)
    db.session.commit()
    for code, title, unit, semester, level in [
        ('CSC101', 'Introduction to Programming', 3, '1', '100'),
        ('CSC102', 'Computer Systems', 3, '2', '100'),
        ('CSC201', 'Data Structures & Algorithms', 4, '1', '200'),
        ('CSC202', 'Databases', 3, '2', '200'),
        ('CSC301', 'Software Engineering', 3, '1', '300'),
        ('CSC302', 'Operating Systems', 3, '2', '300'),
        ('CSC401', 'Artificial Intelligence', 3, '1', '400'),
        ('CSC402', 'Machine Learning', 3, '2', '400'),
        ('CSC303', 'Networks', 3, '1', '300'),
        ('CSC203', 'Algorithms', 3, '2', '200'),
    ]:
        course = Course(code=code, title=title, unit=unit, semester=semester, level=level, lecturer_id=lecturers[0].id)
        db.session.add(course)
    db.session.commit()
    courses = Course.query.all()
    counts = []
    for index in range(1, 81):
        if index <= len(seed.STUDENT_NAMES):
            name = seed.STUDENT_NAMES[index - 1]
        else:
            name = f'Extra Student {index}'
        if index <= 20:
            level = '100'
        elif index <= 40:
            level = '200'
        elif index <= 60:
            level = '300'
        else:
            level = '400'
        eligible = [course for course in courses if course.level == level]
        selected = seed.random.sample(eligible, k=min(4, len(eligible)))
        if len(selected) < 4:
            remaining = 4 - len(selected)
            extra = [c for c in courses if c not in selected]
            extra_selected = seed.random.sample(extra, k=min(remaining, len(extra))) if extra else []
            selected.extend(extra_selected)
        counts.append((index, level, len(eligible), len(selected), [c.code for c in selected]))
    print('Counts by level:')
    from collections import Counter
    print(Counter([c[3] for c in counts]))
    print([c for c in counts if c[3] != 4][:10])
