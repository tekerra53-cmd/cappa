import pytest
from app import create_app
from app.models import User, Student, Course, Result, AcademicSession
from app.extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


def test_user_model(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com', role='student')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        retrieved = User.query.filter_by(username='testuser').first()
        assert retrieved.username == 'testuser'
        assert retrieved.email == 'test@example.com'
        assert retrieved.role == 'student'
        assert retrieved.check_password('password')


def test_student_model(app):
    with app.app_context():
        user = User(username='student', email='student@example.com', role='student')
        db.session.add(user)

        student = Student(
            matric_no='2024/001',
            name='John Doe',
            department='Computer Science',
            level='100',
            user=user
        )
        db.session.add(student)
        db.session.commit()

        retrieved = Student.query.filter_by(matric_no='2024/001').first()
        assert retrieved.name == 'John Doe'
        assert retrieved.user.username == 'student'


def test_course_model(app):
    with app.app_context():
        lecturer = User(username='lecturer', email='lecturer@example.com', role='lecturer')
        db.session.add(lecturer)

        course = Course(
            code='CSC101',
            title='Intro to Programming',
            unit=3,
            semester='1',
            level='100',
            lecturer=lecturer
        )
        db.session.add(course)
        db.session.commit()

        retrieved = Course.query.filter_by(code='CSC101').first()
        assert retrieved.title == 'Intro to Programming'
        assert retrieved.lecturer.username == 'lecturer'


def test_result_computation(app):
    with app.app_context():
        # Create dependencies
        user = User(username='student', email='student@example.com', role='student')
        db.session.add(user)

        student = Student(matric_no='2024/001', name='John Doe', department='CS', level='100', user=user)
        db.session.add(student)

        lecturer = User(username='lecturer', email='lecturer@example.com', role='lecturer')
        db.session.add(lecturer)

        course = Course(code='CSC101', title='Test', unit=3, semester='1', level='100', lecturer=lecturer)
        db.session.add(course)

        session = AcademicSession(name='2024/2025', is_active=True)
        db.session.add(session)

        db.session.commit()

        # Test result computation
        result = Result(
            student=student,
            course=course,
            session=session,
            semester='1',
            ca=30,
            exam=50
        )
        result.compute()

        assert result.total == 80
        assert result.grade == 'A'
        assert result.grade_point == 5.0


def test_session_model(app):
    with app.app_context():
        session = AcademicSession(name='2024/2025', is_active=True)
        db.session.add(session)
        db.session.commit()

        retrieved = AcademicSession.query.filter_by(name='2024/2025').first()
        assert retrieved.is_active == True