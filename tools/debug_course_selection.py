import os
import sys
from pathlib import Path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))
path = root / 'tmp_debug2.sqlite'
if path.exists():
    path.unlink()
os.environ['DATABASE_URL'] = f'sqlite:///{path.resolve()}'
print('DB', path.resolve())
from seed import seed_database
seed_database()
from app import create_app
from app.models import Course, Student, Result
app = create_app()
with app.app_context():
    print('Courses by level:', {lvl: Course.query.filter_by(level=lvl).count() for lvl in ['100','200','300','400']})
    print('Total Students', Student.query.count())
    print('Total Results', Result.query.count())
    one = Student.query.filter_by(matric_no='srms/csc/2024/0001').first()
    if one:
        courses = [c.code for c in Course.query.filter_by(level=one.level).all()]
        print('Eligible courses for student 1', courses)
        print('Student 1 results', [(r.course.code, r.semester, r.total, r.grade) for r in one.results])
    # inspect from seed logic by repeating eligible course selection
    levels = ['100','200','300','400']
    for lvl in levels:
        eligible = Course.query.filter_by(level=lvl).all()
        print(lvl, len(eligible), [c.code for c in eligible])
