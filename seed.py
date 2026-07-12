from app import create_app
from app.extensions import db
from app.models import AcademicSession, Course, Result, Student, User
import random


LECTURER_NAMES = [
    'Dr. Adewale Ogunlade', 'Prof. Ngozi Eze', 'Dr. Ibrahim Suleiman',
    'Dr. Funmilayo Adeyemi', 'Prof. Chukwudi Okonkwo',
]
LECTURER_EMAILS = [
    'adewale.ogunlade@gmail.com', 'ngozi.eze@gmail.com', 'ibrahim.suleiman@gmail.com',
    'funmilayo.adeyemi@gmail.com', 'chukwudi.okonkwo@gmail.com',
]
STUDENT_NAMES = [
    'Adebayo Ogunlesi', 'Chiamaka Nwosu', 'Emeka Okoro', 'Fatima Bello', 'Gideon Musa',
    'Halima Abubakar', 'Ikenna Obi', 'Jumai Adamu', 'Kelechi Okafor', 'Loveth Eze',
    'Musa Danjuma', 'Nkechi Ugwu', 'Oluwaseun Akinlade', 'Patience Okafor', 'Quadri Yusuf',
    'Ruth Bamidele', 'Sadiq Ibrahim', 'Temidayo Akinola', 'Uchenna Eke', 'Victoria Adeleke',
    'Wasiu Lawal', 'Yetunde Salami', 'Zainab Kuta', 'Abubakar Sadiq', 'Bosede Ajayi',
    'Chidi Okafor', 'Deborah Yakubu', 'Efosa Ogie', 'Folake Adewale', 'Godwin Okoro',
    'Hauwa Ibrahim', 'Ifeanyi Nwachukwu', 'Joyce Akpan', 'Kingsley Obi', 'Lilian Okafor',
    'Michael Adeyemi', 'Nancy Eze', 'Obinna Chukwu', 'Precious Ogun', 'Rahmat Hassan',
]

# Generate student emails from names
STUDENT_EMAILS = [name.lower().replace(' ', '.') + '@gmail.com' for name in STUDENT_NAMES]

# Generate student usernames from names (firstname.lastname)
STUDENT_USERNAMES = [name.lower().replace(' ', '.').replace("'", '') for name in STUDENT_NAMES]

# Define realistic performance profiles for students (some high, some average, some struggling)
STUDENT_PERFORMANCE = {
    # High performers (top students)
    'Adebayo Ogunlesi': {'attendance': (8, 10), 'assignment': (16, 20), 'test': (15, 20), 'exam': (40, 50)},
    'Chiamaka Nwosu': {'attendance': (8, 10), 'assignment': (16, 20), 'test': (15, 20), 'exam': (38, 48)},
    'Emeka Okoro': {'attendance': (8, 10), 'assignment': (15, 20), 'test': (14, 20), 'exam': (38, 50)},
    'Fatima Bello': {'attendance': (9, 10), 'assignment': (17, 20), 'test': (16, 20), 'exam': (42, 50)},
    'Gideon Musa': {'attendance': (8, 10), 'assignment': (15, 20), 'test': (14, 19), 'exam': (36, 48)},
    'Halima Abubakar': {'attendance': (9, 10), 'assignment': (16, 20), 'test': (15, 20), 'exam': (40, 50)},
    'Ikenna Obi': {'attendance': (8, 10), 'assignment': (15, 19), 'test': (14, 19), 'exam': (36, 48)},
    'Jumai Adamu': {'attendance': (8, 10), 'assignment': (15, 20), 'test': (14, 20), 'exam': (38, 50)},
    'Kelechi Okafor': {'attendance': (8, 10), 'assignment': (15, 19), 'test': (13, 19), 'exam': (35, 48)},
    'Loveth Eze': {'attendance': (9, 10), 'assignment': (16, 20), 'test': (15, 20), 'exam': (40, 50)},
    # Average performers
    'Musa Danjuma': {'attendance': (7, 10), 'assignment': (12, 18), 'test': (10, 17), 'exam': (30, 45)},
    'Nkechi Ugwu': {'attendance': (7, 10), 'assignment': (12, 18), 'test': (10, 17), 'exam': (30, 44)},
    'Oluwaseun Akinlade': {'attendance': (7, 10), 'assignment': (12, 17), 'test': (10, 16), 'exam': (28, 44)},
    'Patience Okafor': {'attendance': (7, 10), 'assignment': (12, 18), 'test': (10, 17), 'exam': (30, 45)},
    'Quadri Yusuf': {'attendance': (7, 10), 'assignment': (11, 17), 'test': (10, 16), 'exam': (28, 44)},
    'Ruth Bamidele': {'attendance': (8, 10), 'assignment': (13, 18), 'test': (11, 17), 'exam': (32, 45)},
    'Sadiq Ibrahim': {'attendance': (7, 10), 'assignment': (12, 17), 'test': (10, 16), 'exam': (28, 44)},
    'Temidayo Akinola': {'attendance': (7, 10), 'assignment': (12, 18), 'test': (10, 17), 'exam': (30, 45)},
    'Uchenna Eke': {'attendance': (7, 10), 'assignment': (11, 17), 'test': (10, 16), 'exam': (28, 44)},
    'Victoria Adeleke': {'attendance': (8, 10), 'assignment': (13, 18), 'test': (11, 17), 'exam': (32, 45)},
    # Below average / struggling
    'Wasiu Lawal': {'attendance': (6, 9), 'assignment': (10, 15), 'test': (8, 14), 'exam': (22, 38)},
    'Yetunde Salami': {'attendance': (6, 9), 'assignment': (10, 15), 'test': (8, 14), 'exam': (22, 38)},
    'Zainab Kuta': {'attendance': (6, 9), 'assignment': (10, 15), 'test': (8, 13), 'exam': (20, 36)},
    'Abubakar Sadiq': {'attendance': (6, 9), 'assignment': (10, 15), 'test': (8, 14), 'exam': (22, 38)},
    'Bosede Ajayi': {'attendance': (6, 9), 'assignment': (10, 14), 'test': (8, 13), 'exam': (20, 36)},
    'Chidi Okafor': {'attendance': (6, 9), 'assignment': (10, 15), 'test': (8, 14), 'exam': (22, 38)},
    'Deborah Yakubu': {'attendance': (7, 10), 'assignment': (11, 16), 'test': (9, 15), 'exam': (24, 40)},
    'Efosa Ogie': {'attendance': (6, 9), 'assignment': (10, 15), 'test': (8, 14), 'exam': (22, 38)},
    'Folake Adewale': {'attendance': (6, 9), 'assignment': (10, 14), 'test': (8, 13), 'exam': (20, 36)},
    'Godwin Okoro': {'attendance': (6, 9), 'assignment': (10, 15), 'test': (8, 14), 'exam': (22, 38)},
    # Mixed performers
    'Hauwa Ibrahim': {'attendance': (7, 10), 'assignment': (12, 18), 'test': (10, 17), 'exam': (28, 44)},
    'Ifeanyi Nwachukwu': {'attendance': (7, 10), 'assignment': (12, 17), 'test': (10, 16), 'exam': (28, 42)},
    'Joyce Akpan': {'attendance': (8, 10), 'assignment': (14, 19), 'test': (12, 18), 'exam': (34, 48)},
    'Kingsley Obi': {'attendance': (7, 10), 'assignment': (12, 18), 'test': (10, 17), 'exam': (28, 44)},
    'Lilian Okafor': {'attendance': (7, 10), 'assignment': (12, 17), 'test': (10, 16), 'exam': (28, 42)},
    'Michael Adeyemi': {'attendance': (8, 10), 'assignment': (14, 19), 'test': (12, 18), 'exam': (34, 48)},
    'Nancy Eze': {'attendance': (7, 10), 'assignment': (12, 18), 'test': (10, 17), 'exam': (28, 44)},
    'Obinna Chukwu': {'attendance': (7, 10), 'assignment': (12, 17), 'test': (10, 16), 'exam': (28, 42)},
    'Precious Ogun': {'attendance': (8, 10), 'assignment': (14, 19), 'test': (12, 18), 'exam': (34, 48)},
    'Rahmat Hassan': {'attendance': (7, 10), 'assignment': (12, 18), 'test': (10, 17), 'exam': (28, 44)},
}


def _ensure_demo_accounts(app):
    with app.app_context():
        if User.query.filter_by(role='admin').first() is None:
            admin = User()
            admin.username = 'admin'
            admin.email = 'admin@gmail.com'
            admin.role = 'admin'
            admin.set_password('123456')
            db.session.add(admin)

        if User.query.filter_by(role='lecturer').count() >= 5:
            lecturers = User.query.filter_by(role='lecturer').all()
        else:
            lecturers = []
            for index, (name, email) in enumerate(zip(LECTURER_NAMES, LECTURER_EMAILS), start=1):
                username = name.lower().replace('dr. ', '').replace('prof. ', '').replace(' ', '.')
                if User.query.filter_by(username=username).first():
                    continue
                lecturer = User()
                lecturer.username = username
                lecturer.email = email
                lecturer.role = 'lecturer'
                lecturer.set_password('123456')
                lecturer.is_advisor = index in {1, 2, 3}
                db.session.add(lecturer)
                lecturers.append(lecturer)

        if AcademicSession.query.count() == 0:
            sessions = []
            ses1 = AcademicSession()
            ses1.name = '2023/2024'
            ses1.is_active = False
            sessions.append(ses1)
            ses2 = AcademicSession()
            ses2.name = '2024/2025'
            ses2.is_active = True
            sessions.append(ses2)
            db.session.add_all(sessions)

        db.session.commit()

        lecturers = User.query.filter_by(role='lecturer').all()
        if not lecturers:
            raise RuntimeError('No lecturers were created')

        if Course.query.count() == 0:
            course_data = [
                ('CSC101', 'Introduction to Programming', 3, '1', '100'),
                ('CSC201', 'Data Structures & Algorithms', 4, '1', '200'),
                ('CSC301', 'Software Engineering', 3, '1', '300'),
                ('CSC401', 'Artificial Intelligence', 3, '1', '400'),
            ]
            courses = []
            for code, title, unit, semester, level in course_data:
                course = Course()
                course.code = code
                course.title = title
                course.unit = unit
                course.semester = semester
                course.level = level
                course.lecturer_id = lecturers[len(courses) % len(lecturers)].id
                db.session.add(course)
                courses.append(course)
            db.session.commit()
        else:
            courses = Course.query.all()

        if Student.query.count() < 40:
            active_session = AcademicSession.query.filter_by(is_active=True).first()
            if active_session is None:
                raise RuntimeError('No active academic session found')
            dept_map = {
                '100': 'Computer Science',
                '200': 'Computer Science',
                '300': 'Software Engineering',
                '400': 'Information Technology',
            }
            for index, name in enumerate(STUDENT_NAMES[:40], start=1):
                username = STUDENT_USERNAMES[index - 1]
                email = STUDENT_EMAILS[index - 1]
                if User.query.filter_by(username=username).first():
                    continue
                user = User()
                user.username = username
                user.email = email
                user.role = 'student'
                user.set_password('123456')
                db.session.add(user)
                db.session.flush()
                level = '100' if index <= 10 else '200' if index <= 20 else '300' if index <= 30 else '400'
                student = Student()
                student.matric_no = f'srms/csc/{2024 if index <= 20 else 2025}/{index:04d}'
                student.name = name
                student.department = dept_map[level]
                student.level = level
                student.user_id = user.id
                student.temp_password = '123456'
                db.session.add(student)
                db.session.flush()
                eligible_courses = [course for course in courses if course.level == level]
                selected_courses = random.sample(eligible_courses, k=min(2, len(eligible_courses)))
                if not selected_courses:
                    selected_courses = random.sample(courses, k=min(2, len(courses)))
                # Use performance profile if available, otherwise use default ranges
                perf = STUDENT_PERFORMANCE.get(name, {'attendance': (6, 10), 'assignment': (10, 20), 'test': (8, 20), 'exam': (20, 50)})
                for course in selected_courses:
                    result = Result()
                    result.student_id = student.id
                    result.course_id = course.id
                    result.session_id = active_session.id
                    result.semester = course.semester
                    result.attendance = round(random.uniform(*perf['attendance']), 1)
                    result.assignment = round(random.uniform(*perf['assignment']), 1)
                    result.test = round(random.uniform(*perf['test']), 1)
                    result.exam = round(random.uniform(*perf['exam']), 1)
                    result.compute()
                    db.session.add(result)
                db.session.commit()

        db.session.commit()


def seed_database():
    app = create_app()
    _ensure_demo_accounts(app)
    print('Database seeded successfully!')
    print('Admin login: admin / 123456')
    print('Lecturer login: (name-based usernames) / 123456')
    print('  e.g. adewale.ogunlade / 123456')
    print('  e.g. ngozi.eze / 123456')
    print('Student login: (name-based usernames) / 123456')
    print('  e.g. adebayo.ogunlesi / 123456')
    print('  e.g. fatima.bello / 123456')


if __name__ == '__main__':
    seed_database()