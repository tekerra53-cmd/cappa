from faker import Faker
from app import create_app
from app.models import User, Course, Result, AcademicSession
from app.extensions import db
import random

fake = Faker()


def seed_database():
    app = create_app()
    with app.app_context():
        if User.query.first() or Course.query.first() or AcademicSession.query.first():
            print('Database already contains data; skipping seed.')
            return

        db.drop_all()
        db.create_all()

        admin = User()
        admin.username = 'admin'
        admin.email = 'admin@srms.local'
        admin.role = 'admin'
        admin.set_password('admin123')
        db.session.add(admin)

        lecturers = []
        students = []

        sessions = []
        for year in ['2023/2024', '2024/2025']:
            session = AcademicSession()
            session.name = year
            session.is_active = (year == '2024/2025')
            db.session.add(session)
            sessions.append(session)

        db.session.commit()

        courses = []
        course_data = [
            ('CSC101', 'Introduction to Programming', 3, '1', '100'),
            ('CSC102', 'Data Structures', 3, '2', '100'),
            ('CSC201', 'Algorithms', 3, '1', '200'),
            ('CSC202', 'Database Systems', 3, '2', '200'),
            ('CSC301', 'Software Engineering', 3, '1', '300'),
            ('CSC302', 'Web Development', 3, '2', '300'),
            ('CSC401', 'Artificial Intelligence', 3, '1', '400'),
            ('CSC402', 'Project Management', 3, '2', '400'),
            ('MTH101', 'Calculus I', 3, '1', '100'),
            ('MTH102', 'Linear Algebra', 3, '2', '100'),
            ('PHY101', 'Mechanics', 3, '1', '100'),
            ('PHY102', 'Electricity & Magnetism', 3, '2', '100'),
        ]

        for code, title, unit, semester, level in course_data:
            lecturer = random.choice(lecturers) if lecturers else None
            course = Course()
            course.code = code
            course.title = title
            course.unit = unit
            course.semester = semester
            course.level = level
            course.lecturer_id = lecturer.id if lecturer else None
            db.session.add(course)
            courses.append(course)

        if students:
            active_session = next(s for s in sessions if s.is_active)
            for student in students:
                eligible_courses = [c for c in courses if c.level == student.level]
                if not eligible_courses:
                    eligible_courses = courses[:6]

                enrolled_courses = random.sample(eligible_courses, min(len(eligible_courses), random.randint(4, 6)))

                for course in enrolled_courses:
                    attendance = round(random.uniform(0, 10), 1)
                    assignment = round(random.uniform(0, 20), 1)
                    test_score = round(random.uniform(0, 20), 1)
                    exam = round(random.uniform(20, 50), 1)
                    result = Result()
                    result.student_id = student.id
                    result.course_id = course.id
                    result.session_id = active_session.id
                    result.semester = course.semester
                    result.attendance = attendance
                    result.assignment = assignment
                    result.test = test_score
                    result.exam = exam
                    result.compute()
                    db.session.add(result)

                db.session.commit()

        db.session.commit()
        print('Database seeded successfully!')
        print(f'Created: {len(lecturers)} lecturers, {len(students)} students, {len(courses)} courses')
        print('Admin login: admin / admin123')
        print('Lecturer/Student login: any username / pass123')

if __name__ == '__main__':
    seed_database()
