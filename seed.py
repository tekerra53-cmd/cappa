from app import create_app
from app.extensions import db
from app.models import AcademicSession, Course, Result, Student, User
import random


LECTURER_NAMES = [
    'Dr. Adewale Ogunlade', 'Prof. Ngozi Eze', 'Dr. Ibrahim Suleiman',
    'Dr. Funmilayo Adeyemi', 'Prof. Chukwudi Okonkwo', 'Dr. Kemi Adebayo',
    'Dr. Samuel Kuti', 'Prof. Aisha Bello', 'Dr. Emeka Nnaji', 'Dr. Sola Akin',
    'Prof. Peter Obi', 'Dr. Linda Okeke', 'Dr. Uche Nwosu', 'Prof. Adaora Nnamdi',
    'Dr. Tunde Bakare', 'Dr. Grace Ibe',
]
LECTURER_EMAILS = [
    'adewale.ogunlade@gmail.com', 'ngozi.eze@gmail.com', 'ibrahim.suleiman@gmail.com',
    'funmilayo.adeyemi@gmail.com', 'chukwudi.okonkwo@gmail.com', 'kemi.adebayo@gmail.com',
    'samuel.kuti@gmail.com', 'aisha.bello@gmail.com', 'emeka.nnaji@gmail.com', 'sola.akin@gmail.com',
    'peter.obi@gmail.com', 'linda.okeke@gmail.com', 'uche.nwosu@gmail.com', 'adaora.nnamdi@gmail.com',
    'tunde.bakare@gmail.com', 'grace.ibe@gmail.com',
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
        db.create_all()

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

        session_names = {session.name for session in AcademicSession.query.all()}
        if '2023/2024' not in session_names:
            ses1 = AcademicSession()
            ses1.name = '2023/2024'
            ses1.is_active = False
            db.session.add(ses1)
        if '2024/2025' not in session_names:
            ses2 = AcademicSession()
            ses2.name = '2024/2025'
            ses2.is_active = True
            db.session.add(ses2)

        db.session.commit()

        lecturers = User.query.filter_by(role='lecturer').all()
        if not lecturers:
            raise RuntimeError('No lecturers were created')

        course_data = [
            ('CSC101', 'Introduction to Programming', 3, '1', '100'),
            ('CSC102', 'Computer Systems', 3, '2', '100'),
            ('CSC103', 'Digital Logic', 3, '1', '100'),
            ('CSC104', 'Web Development', 3, '2', '100'),
            ('CSC201', 'Data Structures & Algorithms', 4, '1', '200'),
            ('CSC202', 'Databases', 3, '2', '200'),
            ('CSC203', 'Algorithms', 3, '1', '200'),
            ('CSC204', 'Software Architecture', 3, '2', '200'),
            ('CSC301', 'Software Engineering', 3, '1', '300'),
            ('CSC302', 'Operating Systems', 3, '2', '300'),
            ('CSC303', 'Networks', 3, '1', '300'),
            ('CSC304', 'Information Security', 3, '2', '300'),
            ('CSC401', 'Artificial Intelligence', 3, '1', '400'),
            ('CSC402', 'Machine Learning', 3, '2', '400'),
            ('CSC403', 'Cloud Computing', 3, '1', '400'),
            ('CSC404', 'Data Analytics', 3, '2', '400'),
        ]
        courses = []
        for index, (code, title, unit, semester, level) in enumerate(course_data):
            course = Course.query.filter_by(code=code).first()
            if not course:
                course = Course()
                course.code = code
                course.title = title
                course.unit = unit
                course.semester = semester
                course.level = level
                course.lecturer_id = lecturers[index % len(lecturers)].id
                db.session.add(course)
            else:
                course.title = title
                course.unit = unit
                course.semester = semester
                course.level = level
                course.lecturer_id = lecturers[index % len(lecturers)].id
            courses.append(course)
        db.session.commit()

        # Increase student population per request — target 80 students (20 per level)
        STUDENT_TARGET = 80
        if Student.query.count() < STUDENT_TARGET:
            active_session = AcademicSession.query.filter_by(is_active=True).first()
            if active_session is None:
                raise RuntimeError('No active academic session found')
            dept_map = {
                '100': 'Computer Science',
                '200': 'Computer Science',
                '300': 'Software Engineering',
                '400': 'Information Technology',
            }
            course_by_level = {}
            for course in courses:
                course_by_level.setdefault(course.level, []).append(course)

            for index in range(1, STUDENT_TARGET + 1):
                if index <= len(STUDENT_NAMES):
                    name = STUDENT_NAMES[index - 1]
                    username = STUDENT_USERNAMES[index - 1]
                    email = STUDENT_EMAILS[index - 1]
                else:
                    name = f'Extra Student {index}'
                    username = f'extra.student.{index}'
                    email = f'extra.student.{index}@example.com'

                if index <= 20:
                    level = '100'
                elif index <= 40:
                    level = '200'
                elif index <= 60:
                    level = '300'
                else:
                    level = '400'

                year = 2024 if index <= 40 else 2025
                matric_no = f'srms/csc/{year}/{index:04d}'
                existing_student = Student.query.filter_by(matric_no=matric_no).first()
                if existing_student is None:
                    user = User.query.filter_by(username=username).first()
                    if user is None:
                        user = User()
                        user.username = username
                        user.email = email
                        user.role = 'student'
                        user.set_password('123456')
                        db.session.add(user)
                        db.session.flush()

                    student = Student()
                    student.matric_no = matric_no
                    student.name = name
                    student.department = dept_map[level]
                    student.level = level
                    student.user_id = user.id
                    student.temp_password = '123456'
                    db.session.add(student)
                    db.session.flush()
                else:
                    student = existing_student

                eligible_courses = course_by_level.get(level, [])
                if not eligible_courses:
                    continue
                selected_courses = eligible_courses[:4]
                perf = STUDENT_PERFORMANCE.get(name, {'attendance': (6, 10), 'assignment': (10, 20), 'test': (8, 20), 'exam': (20, 50)})
                for course in selected_courses:
                    existing_result = Result.query.filter_by(
                        student_id=student.id,
                        course_id=course.id,
                        session_id=active_session.id,
                        semester=course.semester,
                    ).first()
                    if existing_result:
                        existing_result.attendance = round(random.uniform(*perf['attendance']), 1)
                        existing_result.assignment = round(random.uniform(*perf['assignment']), 1)
                        existing_result.test = round(random.uniform(*perf['test']), 1)
                        existing_result.exam = round(random.uniform(*perf['exam']), 1)
                        existing_result.compute()
                        existing_result.is_approved = True
                        existing_result.approval_status = 'approved'
                        existing_result.approved_by = None
                        existing_result.approved_at = None
                        existing_result.rejection_reason = None
                        db.session.add(existing_result)
                    else:
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
                        result.is_approved = True
                        result.approval_status = 'approved'
                        db.session.add(result)
                db.session.commit()

            # Ensure results include full grade range A-F for demonstration.
            students_for_grades = Student.query.limit(6).all()
            grade_totals = {'A': 75, 'B': 65, 'C': 55, 'D': 47, 'E': 42, 'F': 30}
            sample_course = Course.query.first()
            if sample_course and students_for_grades:
                for stud, (_, total_score) in zip(students_for_grades, grade_totals.items()):
                    attendance = min(10, round(total_score * 0.08, 1))
                    assignment = min(20, round(total_score * 0.20, 1))
                    test = min(20, round(total_score * 0.12, 1))
                    exam = max(0, round(total_score - (attendance + assignment + test), 1))
                    existing_result = Result.query.filter_by(
                        student_id=stud.id,
                        course_id=sample_course.id,
                        session_id=active_session.id,
                        semester=sample_course.semester,
                    ).first()
                    if existing_result is None:
                        result = Result()
                        result.student_id = stud.id
                        result.course_id = sample_course.id
                        result.session_id = active_session.id
                        result.semester = sample_course.semester
                        result.attendance = attendance
                        result.assignment = assignment
                        result.test = test
                        result.exam = exam
                        result.compute()
                        result.is_approved = True
                        result.approval_status = 'approved'
                        db.session.add(result)
                db.session.commit()

            # Guarantee at least 200 approved results for the dashboard and tests.
            while Result.query.count() < 200:
                stud = Student.query.order_by(db.func.random()).first()
                course = Course.query.order_by(db.func.random()).first()
                if not stud or not course:
                    break
                existing = Result.query.filter_by(
                    student_id=stud.id,
                    course_id=course.id,
                    session_id=active_session.id,
                    semester=course.semester,
                ).first()
                if existing:
                    continue
                perf_total = random.randint(20, 90)
                attendance = min(10, round(perf_total * 0.08, 1))
                assignment = min(20, round(perf_total * 0.20, 1))
                test = min(20, round(perf_total * 0.12, 1))
                exam = max(0, round(perf_total - (attendance + assignment + test), 1))
                r = Result()
                r.student_id = stud.id
                r.course_id = course.id
                r.session_id = active_session.id
                r.semester = course.semester
                r.attendance = attendance
                r.assignment = assignment
                r.test = test
                r.exam = exam
                r.compute()
                r.is_approved = True
                r.approval_status = 'approved'
                db.session.add(r)
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