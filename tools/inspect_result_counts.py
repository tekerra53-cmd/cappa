import os
import sys
from pathlib import Path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))
os.environ['DATABASE_URL'] = f'sqlite:///{(root / "tmp_debug2.sqlite").resolve()}'
from app import create_app
from app.extensions import db
from app.models import Student, Result
app = create_app()
with app.app_context():
    rows = db.session.execute('SELECT student_id, COUNT(*) FROM result GROUP BY student_id ORDER BY student_id').all()
    for student_id, count in rows[:20]:
        student = Student.query.get(student_id)
        print(student_id, student.matric_no if student else None, count)
    print('total rows', sum(count for _, count in rows))
