from ..models.course import Course
from ..models.user import User
from ..models.student import Student
from ..models.session import AcademicSession
from ..models.result import Result
from ..models.resit_request import ResitRequest
from ..models.enrollment import Enrollment
from ..extensions import db


def create_user(username, email, password, role):
    # Validate uniqueness to provide clearer errors to the caller
    if User.query.filter_by(username=username).first():
        raise ValueError('Username already exists')
    if User.query.filter_by(email=email).first():
        raise ValueError('Email already exists')

    # Construct the model without calling a positional/keyword init (helps static analyzers)
    u = User()
    u.username = username
    u.email = email
    u.role = role
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u





def create_course(code, title, unit, semester, level, lecturer_id):
    if Course.query.filter_by(code=code).first():
        raise ValueError('Course code already exists')
    c = Course()
    c.code = code
    c.title = title
    c.unit = unit
    c.semester = semester
    c.level = level
    c.lecturer_id = lecturer_id
    db.session.add(c)
    db.session.commit()
    return c


def create_session(name):
    if AcademicSession.query.filter_by(name=name).first():
        raise ValueError('Session exists')
    s = AcademicSession()
    s.name = name
    s.is_active = False
    db.session.add(s)
    db.session.commit()
    return s


def activate_session(session_id):
    AcademicSession.query.update({AcademicSession.is_active: False})
    s = AcademicSession.query.get(session_id)
    if not s:
        raise ValueError('Session not found')
    s.is_active = True
    approved_requests = ResitRequest.query.filter_by(status='approved', enrolled_session_id=None).all()
    for req in approved_requests:
        existing = Enrollment.query.filter_by(student_id=req.student_id, course_id=req.course_id).first()
        if not existing:
            db.session.add(Enrollment(req.student_id, req.course_id))
        req.status = 'enrolled'
        # ensure s is present (checked above)
        req.enrolled_session_id = s.id
    db.session.commit()
    return s
