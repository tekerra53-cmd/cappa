from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from ..models.course import Course
from ..models.student import Student
from ..models.result import Result
from ..models.session import AcademicSession
from ..models.resit_request import ResitRequest
from ..models.advisor_request import AdvisorStudentListRequest
from ..models.notification import Notification
from ..models.advisor_result_submission import AdvisorResultSubmission
from ..models.user import User
from sqlalchemy import or_
from ..extensions import db
from .forms import ResultEntryForm, StudentCreateForm
from .services import save_result, get_active_session, create_student

lecturer_bp = Blueprint('lecturer', __name__)

def lecturer_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'lecturer':
            flash('Lecturer access required', 'warning')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)

    return wrapper


def advisor_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'lecturer' or not current_user.is_advisor:
            flash('Advisor access required', 'warning')
            return redirect(url_for('lecturer.dashboard'))
        return func(*args, **kwargs)

    return wrapper


@lecturer_bp.route('/dashboard')
@login_required
@lecturer_required
def dashboard():
    courses = Course.query.filter_by(lecturer_id=current_user.id).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    return render_template('lecturer/dashboard.html', courses=courses, notifications=notifications)


@lecturer_bp.route('/course/<int:course_id>/results', methods=['GET', 'POST'])
@login_required
@lecturer_required
def course_results(course_id):
    course = Course.query.get_or_404(course_id)
    if course.lecturer_id != current_user.id:
        flash('Not your course', 'danger')
        return redirect(url_for('lecturer.dashboard'))

    session = get_active_session()
    if not session:
        flash('No active session, ask admin to activate one', 'warning')
        return redirect(url_for('lecturer.dashboard'))

    students = Student.query.order_by(Student.name).all()
    results = Result.query.filter_by(course_id=course.id, session_id=session.id).all()

    if request.method == 'POST':
        student_id_val = request.form.get('student_id')
        attendance_val = request.form.get('attendance')
        assignment_val = request.form.get('assignment')
        test_val = request.form.get('test')
        exam_val = request.form.get('exam')
        
        if not student_id_val or not attendance_val or not assignment_val or not test_val or not exam_val:
            flash('All fields are required', 'danger')
            return redirect(url_for('lecturer.course_results', course_id=course.id))
        
        student_id = int(student_id_val)
        attendance = float(attendance_val)
        assignment = float(assignment_val)
        test = float(test_val)
        exam_score = float(exam_val)

        try:
            save_result(student_id, course.id, session.id, course.semester, attendance, assignment, test, exam_score)
            flash('Result saved', 'success')
            return redirect(url_for('lecturer.course_results', course_id=course.id))
        except Exception as e:
            flash(str(e), 'danger')

    results = Result.query.filter_by(course_id=course.id, session_id=session.id).all()
    form = ResultEntryForm()
    return render_template('lecturer/course_results.html', course=course, students=students, results=results, form=form, session=session)


@lecturer_bp.route('/advisor/requests')
@login_required
@advisor_required
def advisor_requests():
    level = current_user.advisor_level
    requests = ResitRequest.query.join(Student).filter(
        Student.level == level,
        ResitRequest.status == 'pending'
    ).order_by(ResitRequest.requested_at.desc()).all()
    return render_template('lecturer/advisor_requests.html', requests=requests, level=level)


@lecturer_bp.route('/advisor/requests/<int:request_id>/approve', methods=['POST'])
@login_required
@advisor_required
def approve_resit_request(request_id):
    req = ResitRequest.query.get_or_404(request_id)
    if req.student.level != current_user.advisor_level:
        flash('Not authorized for this request', 'danger')
        return redirect(url_for('lecturer.advisor_requests'))
    req.status = 'approved'
    req.reviewed_by = current_user.id
    req.reviewed_at = db.func.now()
    db.session.commit()
    flash('Resit request approved. Auto registration will occur when the session is activated.', 'success')
    return redirect(url_for('lecturer.advisor_requests'))


@lecturer_bp.route('/advisor/requests/<int:request_id>/reject', methods=['POST'])
@login_required
@advisor_required
def reject_resit_request(request_id):
    req = ResitRequest.query.get_or_404(request_id)
    if req.student.level != current_user.advisor_level:
        flash('Not authorized for this request', 'danger')
        return redirect(url_for('lecturer.advisor_requests'))
    req.status = 'rejected'
    req.reviewed_by = current_user.id
    req.reviewed_at = db.func.now()
    db.session.commit()
    flash('Resit request rejected.', 'info')
    return redirect(url_for('lecturer.advisor_requests'))


@lecturer_bp.route('/advisor/results')
@login_required
@advisor_required
def advisor_results():
    level = current_user.advisor_level
    session_name = request.args.get('session')
    semester = request.args.get('semester')
    department = request.args.get('department')
    search_query = request.args.get('q', '').strip()
    query = Result.query.join(Student).filter(Student.level == level)

    if session_name:
        session = AcademicSession.query.filter_by(name=session_name).first()
        if session:
            query = query.filter(Result.session_id == session.id)
    if semester:
        query = query.filter(Result.semester == semester)
    if department:
        query = query.filter(Student.department == department)
    if search_query:
        query = query.filter(Student.name.ilike(f"%{search_query}%"))

    results = query.order_by(Result.student_id).all()
    student_query = Student.query.filter_by(level=level)
    if department:
        student_query = student_query.filter_by(department=department)
    if search_query:
        student_query = student_query.filter(Student.name.ilike(f"%{search_query}%"))
    students = student_query.order_by(Student.name).all()
    student_results = {}
    student_results_payload = {}
    for r in results:
        student_results.setdefault(r.student_id, []).append(r)
        payload = student_results_payload.setdefault(r.student_id, [])
        payload.append({
            'course': f"{r.course.code} - {r.course.title}",
            'attendance': r.attendance,
            'assignment': r.assignment,
            'test': r.test,
            'exam': r.exam,
            'total': r.total,
            'grade': r.grade,
            'grade_point': r.grade_point
        })
    sessions = AcademicSession.query.all()
    departments = [d[0] for d in db.session.query(Student.department).filter_by(level=level).distinct().order_by(Student.department).all()]
    ready_info = {}
    if session_name and semester and department:
        session = AcademicSession.query.filter_by(name=session_name).first()
        if session:
            students = Student.query.filter_by(level=level, department=department).all()
            courses = Course.query.filter_by(level=level, semester=semester).all()
            expected = len(students) * len(courses)
            student_ids = [s.id for s in students]
            course_ids = [c.id for c in courses]
            actual = 0
            if student_ids and course_ids:
                actual = Result.query.filter(
                    Result.student_id.in_(student_ids),
                    Result.course_id.in_(course_ids),
                    Result.session_id == session.id,
                    Result.semester == semester
                ).count()
            ready_info = {
                'expected': expected,
                'actual': actual,
                'ready': expected > 0 and actual >= expected,
                'missing_total': expected - actual if expected > actual else 0
            }
    return render_template(
        'lecturer/advisor_results.html',
        results=results,
        students=students,
        student_results=student_results,
        student_results_payload=student_results_payload,
        level=level,
        sessions=sessions,
        departments=departments,
        ready_info=ready_info,
        search_query=search_query
    )


@lecturer_bp.route('/advisor/results/submit', methods=['POST'])
@login_required
@advisor_required
def submit_results_to_admin():
    if not current_user.advisor_level:
        flash('No advisor level assigned.', 'warning')
        return redirect(url_for('lecturer.advisor_results'))

    session_name = request.form.get('session', '').strip()
    semester = request.form.get('semester', '').strip()
    department = request.form.get('department', '').strip()
    note = (request.form.get('note') or '').strip()

    session = AcademicSession.query.filter_by(name=session_name).first()
    if not session:
        flash('Select a valid session to submit.', 'warning')
        return redirect(url_for('lecturer.advisor_results'))
    if not semester:
        flash('Select a semester to submit.', 'warning')
        return redirect(url_for('lecturer.advisor_results', session=session_name))
    if not department:
        flash('Select a department to submit.', 'warning')
        return redirect(url_for('lecturer.advisor_results', session=session_name, semester=semester))

    existing = AdvisorResultSubmission.query.filter_by(
        advisor_id=current_user.id,
        level=current_user.advisor_level,
        department=department,
        session_id=session.id,
        semester=semester,
        status='advisor_submitted'
    ).first()
    if existing:
        flash('This submission is already sent to admin.', 'info')
        return redirect(url_for('lecturer.advisor_results', session=session_name, semester=semester, department=department))

    # completeness check: all students in level/department must have results for all courses in level/semester
    students = Student.query.filter_by(level=current_user.advisor_level, department=department).all()
    courses = Course.query.filter_by(level=current_user.advisor_level, semester=semester).all()
    expected = len(students) * len(courses)
    if expected == 0:
        flash('No students or courses found for this level/department/semester.', 'warning')
        return redirect(url_for('lecturer.advisor_results', session=session_name, semester=semester, department=department))

    student_ids = [s.id for s in students]
    course_ids = [c.id for c in courses]
    actual = Result.query.filter(
        Result.student_id.in_(student_ids),
        Result.course_id.in_(course_ids),
        Result.session_id == session.id,
        Result.semester == semester
    ).count()
    if actual < expected:
        missing = expected - actual
        flash(f'Submission blocked: {missing} result(s) missing for this level/department/semester.', 'warning')
        return redirect(url_for('lecturer.advisor_results', session=session_name, semester=semester, department=department))

    submission = AdvisorResultSubmission(
        advisor_id=current_user.id,
        level=current_user.advisor_level or '',
        department=department,
        session_id=session.id,
        semester=semester,
        status='advisor_submitted',
        note=note if note else None
    )
    db.session.add(submission)
    db.session.commit()
    flash('Results submitted to admin for approval.', 'success')
    return redirect(url_for('lecturer.advisor_results', session=session_name, semester=semester, department=department))


@lecturer_bp.route('/advisor/list-requests')
@login_required
@advisor_required
def advisor_list_requests():
    requests = AdvisorStudentListRequest.query.filter_by(
        advisor_id=current_user.id
    ).order_by(AdvisorStudentListRequest.requested_at.desc()).all()
    return render_template('lecturer/advisor_list_requests.html', requests=requests)


@lecturer_bp.route('/advisor/list-requests/<int:request_id>/students.csv')
@login_required
@advisor_required
def export_advisor_students_csv(request_id):
    req = AdvisorStudentListRequest.query.get_or_404(request_id)
    if req.advisor_id != current_user.id:
        flash('Not authorized for this request', 'danger')
        return redirect(url_for('lecturer.advisor_list_requests'))

    level = current_user.advisor_level
    if not level:
        flash('No advisor level assigned.', 'warning')
        return redirect(url_for('lecturer.advisor_list_requests'))

    students = Student.query.filter_by(level=level).order_by(Student.name).all()
    output = []
    output.append('Name,Matric,Email,Department,Level,Advisor')
    for s in students:
        email = s.user.email if s.user else ''
        row = [
            s.name.replace(',', ' '),
            s.matric_no.replace(',', ' '),
            email.replace(',', ' '),
            s.department.replace(',', ' '),
            s.level.replace(',', ' '),
            current_user.username.replace(',', ' ')
        ]
        output.append(','.join(row))

    csv_data = '\n'.join(output)
    import os
    active_session = AcademicSession.query.filter_by(is_active=True).first()
    session_name = active_session.name if active_session else 'no_session'
    semester = request.args.get('semester') or 'all'
    safe_session = session_name.replace('/', '-').replace('\\', '-').replace(' ', '_')
    safe_semester = str(semester).replace('/', '-').replace('\\', '-').replace(' ', '_')
    folder = os.path.join(current_app.instance_path, 'advisor_lists', safe_session, safe_semester)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"advisor_{current_user.username}_request_{req.id}.csv")
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(csv_data)

    req.csv_path = filepath
    if req.status == 'approved':
        req.status = 'completed'
    req.responded_at = db.func.now()
    db.session.commit()

    return send_file(filepath, as_attachment=True)


@lecturer_bp.route('/advisor/list-requests/<int:request_id>/approve', methods=['POST'])
@login_required
@advisor_required
def approve_list_request(request_id):
    req = AdvisorStudentListRequest.query.get_or_404(request_id)
    if req.advisor_id != current_user.id:
        flash('Not authorized for this request', 'danger')
        return redirect(url_for('lecturer.advisor_list_requests'))
    req.status = 'approved'
    req.responded_at = db.func.now()
    db.session.commit()
    flash('Student list request approved.', 'success')
    return redirect(url_for('lecturer.advisor_list_requests'))


@lecturer_bp.route('/advisor/list-requests/<int:request_id>/reject', methods=['POST'])
@login_required
@advisor_required
def reject_list_request(request_id):
    req = AdvisorStudentListRequest.query.get_or_404(request_id)
    if req.advisor_id != current_user.id:
        flash('Not authorized for this request', 'danger')
        return redirect(url_for('lecturer.advisor_list_requests'))
    req.status = 'rejected'
    req.responded_at = db.func.now()
    db.session.commit()
    flash('Student list request rejected.', 'info')
    return redirect(url_for('lecturer.advisor_list_requests'))


@lecturer_bp.route('/advisor/list-requests/<int:request_id>/complete', methods=['POST'])
@login_required
@advisor_required
def complete_list_request(request_id):
    req = AdvisorStudentListRequest.query.get_or_404(request_id)
    if req.advisor_id != current_user.id:
        flash('Not authorized for this request', 'danger')
        return redirect(url_for('lecturer.advisor_list_requests'))
    if req.status != 'approved':
        flash('Only approved requests can be completed.', 'warning')
        return redirect(url_for('lecturer.advisor_list_requests'))
    req.status = 'completed'
    req.responded_at = db.func.now()
    db.session.commit()
    flash('Student list submitted to admin.', 'success')
    return redirect(url_for('lecturer.advisor_list_requests'))


@lecturer_bp.route('/advisor/create-student', methods=['GET', 'POST'])
@login_required
@advisor_required
def create_student_route():
    if not current_user.advisor_level:
        flash('No advisor level assigned.', 'warning')
        return redirect(url_for('lecturer.dashboard'))
    form = StudentCreateForm()
    if form.validate_on_submit():
        try:
            student, password = create_student(form.name.data, None, form.department.data, current_user.advisor_level, form.email.data)
            flash(f'Student {student.name} (matric {student.matric_no}) created for level {current_user.advisor_level}. Password: {password}', 'success')
            form = StudentCreateForm()  # Reset form
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Creation failed: {str(e)}', 'danger')
    return render_template('lecturer/create_student.html', form=form, level=current_user.advisor_level)


@lecturer_bp.route('/advisor/students')
@login_required
@advisor_required
def advisor_students():
    level = current_user.advisor_level
    search_query = request.args.get('q', '').strip()
    query = Student.query.filter_by(level=level)
    if search_query:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{search_query}%"),
                Student.matric_no.ilike(f"%{search_query}%")
            )
        )
    students = query.order_by(Student.name).all()
    return render_template('lecturer/advisor_students.html', students=students, level=level, search_query=search_query)
