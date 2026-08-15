import os
from pathlib import Path
DB = Path('tmp_debug.sqlite')
if DB.exists():
    DB.unlink()
os.environ['DATABASE_URL'] = f'sqlite:///{DB.absolute()}'
from seed import seed_database
seed_database()
from app import create_app
from app.extensions import db
from app.models import User, Student, Result, Course, AcademicSession
app = create_app()
with app.app_context():
    print('Users total:', User.query.count())
    print('Lecturers:', User.query.filter_by(role='lecturer').count())
    print('Students:', Student.query.count())
    print('Courses:', Course.query.count())
    print('AcademicSessions:', AcademicSession.query.count())
    print('Results:', Result.query.count())
