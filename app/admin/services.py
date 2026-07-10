from ..models.course import Course
from ..models.user import User
from ..models.student import Student
from ..models.session import AcademicSession
from ..models.result import Result
from ..models.resit_request import ResitRequest
from ..models.enrollment import Enrollment
from ..extensions import db


def create_user(username, email, password, role):
    u = User(username=username, email=email, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u





def create_course(code, title, unit, semester, level, lecturer_id):
    if Course.query.filter_by(code=code).first():
        raise ValueError('Course code already exists')
    c = Course(code=code, title=title, unit=unit, semester=semester, level=level, lecturer_id=lecturer_id)
    db.session.add(c)
    db.session.commit()
    return c


def create_session(name):
    if AcademicSession.query.filter_by(name=name).first():
        raise ValueError('Session exists')
    s = AcademicSession(name=name, is_active=False)
    db.session.add(s)
    db.session.commit()
    return s


def activate_session(session_id):
    AcademicSession.query.update({AcademicSession.is_active: False})
    s = AcademicSession.query.get(session_id)
    s.is_active = True
    approved_requests = ResitRequest.query.filter_by(status='approved', enrolled_session_id=None).all()
    for req in approved_requests:
        existing = Enrollment.query.filter_by(student_id=req.student_id, course_id=req.course_id).first()
        if not existing:
            db.session.add(Enrollment(student_id=req.student_id, course_id=req.course_id))
        req.status = 'enrolled'
        req.enrolled_session_id = s.id
    db.session.commit()
    return s
