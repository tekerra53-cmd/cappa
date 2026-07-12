from ..models.student import Student
from ..models.result import Result
from ..models.session import AcademicSession


def get_student_by_user(user_id):
    return Student.query.filter_by(user_id=user_id).first()


def get_student_results(student_id, session_name=None, semester=None):
    query = Result.query.filter_by(student_id=student_id)
    query = query.filter((Result.approval_status == 'approved') | (Result.is_approved.is_(True)))
    if session_name:
        session = AcademicSession.query.filter_by(name=session_name).first()
        if session:
            query = query.filter_by(session_id=session.id)
    if semester:
        query = query.filter_by(semester=semester)
    return query.order_by(Result.id).all()
