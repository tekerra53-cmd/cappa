from ..models.result import Result
from ..models.result_approval_history import ResultApprovalHistory
from ..models.session import AcademicSession
from ..models.user import User
from ..models.student import Student
from ..extensions import db


def save_result(student_id, course_id, session_id, semester, attendance, assignment, test, exam):
    res = Result.query.filter_by(student_id=student_id, course_id=course_id, session_id=session_id, semester=semester).first()
    if not res:
        res = Result(student_id=student_id, course_id=course_id, session_id=session_id, semester=semester)
    res.attendance = attendance
    res.assignment = assignment
    res.test = test
    res.exam = exam
    res.compute()
    res.is_approved = False
    res.approval_status = 'pending'
    res.rejection_reason = None
    res.approved_by = None
    res.approved_at = None
    db.session.add(res)
    db.session.flush()
    history = ResultApprovalHistory(
        result_id=res.id,
        action='submitted',
        note='Result submitted by lecturer'
    )
    db.session.add(history)
    db.session.commit()
    return res


def get_active_session():
    return AcademicSession.query.filter_by(is_active=True).first()

def create_student(name, matric_no, department, level, email=None, initial_password=None):
    dept_abbr_map = {
        'computer science': 'CSC',
        'cyber': 'CYB',
        'information technology': 'IT',
        'accounting': 'ACC',
        'business admin': 'BUS',
    }
    dept_abbr = dept_abbr_map.get(department.lower(), department[:3].upper())
    # Auto-generate matric if not provided
    if not matric_no:
        from datetime import datetime
        year = str(datetime.now().year)[-2:]
        prefix = f"srms/{dept_abbr.lower()}/{year}/"
        existing = Student.query.filter(Student.matric_no.like(f"{prefix}%")).all()
        max_id = 0
        for s in existing:
            try:
                tail = s.matric_no.split('/')[-1]
                max_id = max(max_id, int(tail))
            except Exception:
                continue
        student_num = f"{max_id + 1:04d}"
        matric_no = f"{prefix}{student_num}"
    else:
        parts = matric_no.split('/')
        if len(parts) != 4 or parts[0].lower() != 'srms':
            raise ValueError('Matric number format must be srms/dept/year/id')
    
    if Student.query.filter_by(matric_no=matric_no).first():
        raise ValueError('Matric number already exists')
    username = matric_no.lower().replace('/', '').replace('-', '').replace(' ', '')

    if User.query.filter_by(username=username).first():
        raise ValueError('Student username already exists')
    if email and User.query.filter_by(email=email).first():
        raise ValueError('Email already in use')

    student_user = User(
        username=username,
        email=email or f'{username}@srms.local',
        role='student',
        force_password_change=True
    )

    import string
    import random
    if initial_password:
        password = initial_password
    else:
        letters = ''.join(random.choices(string.ascii_letters, k=4))
        digits = ''.join(random.choices(string.digits, k=3))
        password = letters + digits


    student_user.set_password(password)

    s = Student(name=name, matric_no=matric_no, department=department, level=level, user=student_user, temp_password=password)

    db.session.add(student_user)
    db.session.add(s)
    db.session.commit()

    return s, password

