import os
import sys
from pathlib import Path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))
path = root / 'tmp_clean.sqlite'
if path.exists():
    path.unlink()
os.environ['DATABASE_URL'] = f'sqlite:///{path.resolve()}'
from seed import seed_database
seed_database()
from app import create_app
from app.models import Course, Student, Result
app = create_app()
with app.app_context():
    print('Courses:', Course.query.count())
    print('Courses by level:', {lvl: Course.query.filter_by(level=lvl).count() for lvl in ['100','200','300','400']})
    print('Students:', Student.query.count())
    print('Results:', Result.query.count())
    print('Approved results:', Result.query.filter_by(approval_status='approved').count())
    print('Approved by is_approved flag:', Result.query.filter_by(is_approved=True).count())
    print('Approval status values:', {r.approval_status for r in Result.query.limit(10).all()})
    print('By student counts:', sorted({len(s.results) for s in Student.query.all()}))
    for idx, s in enumerate(Student.query.order_by(Student.id).limit(10).all(), 1):
        print(f'Student {idx} {s.matric_no} {s.level} has {len(s.results)} results: {[ (r.course.code, r.semester, r.total, r.is_approved, r.approval_status) for r in s.results ]}')
