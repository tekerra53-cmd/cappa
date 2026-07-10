import pytest
from app import create_app
from app.models import User, Student, Course, Result, AcademicSession
from app.core.utils import calculate_gpa, calculate_grade
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


def test_calculate_grade():
    # Test various grade calculations
    total, grade, gp = calculate_grade(5, 20, 5, 50)  # 80 total
    assert total == 80
    assert grade == 'A'
    assert gp == 5.0

    total, grade, gp = calculate_grade(2, 15, 8, 40)  # 65 total
    assert total == 65
    assert grade == 'B'
    assert gp == 4.0

    total, grade, gp = calculate_grade(1, 10, 10, 29)  # 50 total
    assert total == 50
    assert grade == 'C'
    assert gp == 3.0

    total, grade, gp = calculate_grade(1, 9, 10, 30)  # 50 total (boundary)
    assert total == 50
    assert grade == 'C'
    assert gp == 3.0

    total, grade, gp = calculate_grade(2, 8, 10, 30)  # 50 total
    assert total == 50
    assert grade == 'C'
    assert gp == 3.0

    total, grade, gp = calculate_grade(1, 6, 10, 27)  # 44 total
    assert total == 44
    assert grade == 'E'
    assert gp == 1.0

    total, grade, gp = calculate_grade(0, 5, 5, 20)  # 30 total
    assert total == 30
    assert grade == 'F'
    assert gp == 0.0


def test_calculate_gpa(app):
    with app.app_context():
        # Create test data
        user = User(username='student', email='student@example.com', role='student')
        db.session.add(user)

        student = Student(matric_no='2024/001', name='John Doe', department='CS', level='100', user=user)
        db.session.add(student)

        lecturer = User(username='lecturer', email='lecturer@example.com', role='lecturer')
        db.session.add(lecturer)

        courses = []
        for i in range(3):
            course = Course(
                code=f'CSC10{i}',
                title=f'Course {i}',
                unit=3,
                semester='1',
                level='100',
                lecturer=lecturer
            )
            db.session.add(course)
            courses.append(course)

        session = AcademicSession(name='2024/2025', is_active=True)
        db.session.add(session)

        db.session.commit()

        # Create results with known GPAs
        results = []
        for i, course in enumerate(courses):
            result = Result(
                student=student,
                course=course,
                session=session,
                semester='1',
                ca=30,  # Will give A grade (5.0 GP)
                exam=50
            )
            result.compute()
            db.session.add(result)
            results.append(result)

        db.session.commit()

        # Test GPA calculation
        gpa = calculate_gpa(results)
        expected_gpa = (5.0 * 3 + 5.0 * 3 + 5.0 * 3) / (3 + 3 + 3)  # All A's
        assert gpa == expected_gpa


def test_result_workflow(app):
    with app.app_context():
        # Create complete workflow test
        user = User(username='student', email='student@example.com', role='student')
        db.session.add(user)

        student = Student(matric_no='2024/001', name='John Doe', department='CS', level='100', user=user)
        db.session.add(student)

        lecturer = User(username='lecturer', email='lecturer@example.com', role='lecturer')
        db.session.add(lecturer)

        course = Course(code='CSC101', title='Test Course', unit=3, semester='1', level='100', lecturer=lecturer)
        db.session.add(course)

        session = AcademicSession(name='2024/2025', is_active=True)
        db.session.add(session)

        db.session.commit()

        # Create and save result
        result = Result(
            student=student,
            course=course,
            session=session,
            semester='1',
            attendance=5,
            assignment=15,
            test=15,
            exam=45
        )
        result.compute()
        db.session.add(result)
        db.session.commit()

        # Verify result was saved correctly
        saved_result = Result.query.filter_by(student=student, course=course).first()
        assert saved_result is not None
        assert saved_result.total == 80
        assert saved_result.grade == 'A'
        assert saved_result.grade_point == 5.0