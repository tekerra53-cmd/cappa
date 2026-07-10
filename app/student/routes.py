from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .services import get_student_by_user, get_student_results
from ..models.session import AcademicSession
from ..models.result import Result
from ..models.resit_request import ResitRequest
from ..extensions import db

student_bp = Blueprint('student', __name__)


def student_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)

    return wrapper


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    student = get_student_by_user(current_user.id)
    if not student:
        return render_template('student/dashboard.html', results=[], gpa=0, cgpa=0)

    session_name = request.args.get('session')
    semester = request.args.get('semester')
    results = get_student_results(student.id, session_name=session_name, semester=semester)
    all_results = get_student_results(student.id)
    resit_requests = ResitRequest.query.filter_by(student_id=student.id).order_by(ResitRequest.requested_at.desc()).all()
    resit_by_course = {}
    for req in resit_requests:
        if req.course_id not in resit_by_course:
            resit_by_course[req.course_id] = req

    gpa = cgpa = 0
    from ..core.utils import calculate_gpa
    if results:
        gpa = calculate_gpa(results)
    if all_results:
        cgpa = calculate_gpa(all_results)

    sessions = AcademicSession.query.all()
    return render_template(
        'student/dashboard.html',
        results=results,
        gpa=gpa,
        cgpa=cgpa,
        sessions=sessions,
        resit_by_course=resit_by_course
    )


@student_bp.route('/resit/request', methods=['POST'])
@login_required
@student_required
def request_resit():
    student = get_student_by_user(current_user.id)
    if not student:
        return redirect(url_for('student.dashboard'))

    try:
        course_id = int(request.form.get('course_id'))
    except Exception:
        flash('Invalid request', 'danger')
        return redirect(url_for('student.dashboard'))

    failed = Result.query.filter_by(student_id=student.id, course_id=course_id).filter(Result.grade_point == 0).first()
    if not failed:
        flash('You can only request a resit for failed courses.', 'warning')
        return redirect(url_for('student.dashboard'))

    existing = ResitRequest.query.filter_by(student_id=student.id, course_id=course_id).order_by(ResitRequest.requested_at.desc()).first()
    if existing and existing.status in ('pending', 'approved', 'enrolled'):
        flash('Resit request already submitted.', 'info')
        return redirect(url_for('student.dashboard'))

    req = ResitRequest(
        student_id=student.id,
        course_id=course_id,
        status='pending',
        target_semester=failed.course.semester if failed.course else None
    )
    db.session.add(req)
    db.session.commit()
    flash('Resit request submitted to your course advisor.', 'success')
    return redirect(url_for('student.dashboard'))

