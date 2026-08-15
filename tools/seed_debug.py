import os
import sys
from pathlib import Path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))
os.environ['DATABASE_URL'] = f'sqlite:///{(root / "tmp_debug.sqlite").resolve()}'
from seed import _ensure_demo_accounts
from app import create_app
from app.extensions import db
from app.models import Course, Student, Result, AcademicSession, User
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    _ensure_demo_accounts(app)
    print('courses total', Course.query.count())
    for lvl in ['100','200','300','400']:
        print('level', lvl, 'count', Course.query.filter_by(level=lvl).count())
    
    students = Student.query.order_by(Student.id).all()
    print('students count after seed step', len(students))
    if students:
        first = students[0]
        print('first student', first.matric_no, first.level)
        eligible = [c for c in Course.query.all() if c.level == first.level]
        print('eligible count', len(eligible), [c.code for c in eligible])
    
    from seed import STUDENT_TARGET, STUDENT_NAMES, STUDENT_USERNAMES, STUDENT_EMAILS, STUDENT_PERFORMANCE
    print('student_names len', len(STUDENT_NAMES), 'target', STUDENT_TARGET)
    
    # simulate selection logic for first 10 students
    all_courses = Course.query.all()
    for index in range(1, 11):
        if index <= len(STUDENT_NAMES):
            name = STUDENT_NAMES[index - 1]
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
        eligible = [course for course in all_courses if course.level == level]
        selected = []
        if len(eligible) >= 4:
            selected = list(__import__('random').sample(eligible, k=4))
        else:
            selected = list(__import__('random').sample(eligible, k=len(eligible)))
            remaining = 4 - len(selected)
            extra = [c for c in all_courses if c not in selected]
            if extra:
                selected.extend(__import__('random').sample(extra, k=min(remaining, len(extra))))
        print('student', index, 'level', level, 'eligible', len(eligible), 'selected', [c.code for c in selected])
    
    print('total results after seed', Result.query.count())
    print('sample first student results', [(r.course.code, r.semester, r.total) for r in first.results])
