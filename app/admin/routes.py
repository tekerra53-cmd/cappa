from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from ..models.user import User
from ..models.student import Student
from ..models.advisor_request import AdvisorStudentListRequest
from ..models.course import Course
from ..models.session import AcademicSession
from ..models.result import Result
from ..models.result_approval_history import ResultApprovalHistory
from ..models.notification import Notification
from ..models.advisor_result_submission import AdvisorResultSubmission
from .forms import UserCreateForm, CourseForm, AcademicSessionForm, AdvisorAssignForm, AdvisorListRequestForm
from .services import create_user, create_course, create_session, activate_session
from ..extensions import db

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'warning')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.count()
    completed_submissions = AdvisorStudentListRequest.query.filter_by(status='completed').count()
    students = Student.query.count()
    courses = Course.query.count()
    sessions = AcademicSession.query.count()
    return render_template('admin/dashboard.html', users=users, students=students, courses=courses, sessions=sessions, completed_submissions=completed_submissions)


@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def user_list():
    form = UserCreateForm()
    if form.validate_on_submit():
        try:
            if form.role.data != 'lecturer':
                flash('Admins can only create lecturer accounts.', 'warning')
                return redirect(url_for('admin.user_list'))
            create_user(form.username.data, form.email.data, form.password.data, form.role.data)
            flash('User created', 'success')
            return redirect(url_for('admin.user_list'))
        except Exception as e:
            flash(str(e), 'danger')

    search_query = request.args.get('q', '').strip()
    users_query = User.query.filter_by(role='lecturer')
    if search_query:
        users_query = users_query.filter(
            or_(
                User.username.ilike(f"%{search_query}%"),
                User.email.ilike(f"%{search_query}%")
            )
        )
    users = users_query.order_by(User.username).all()
    advisor_form = AdvisorAssignForm()
    lecturers = User.query.filter_by(role='lecturer').order_by(User.username).all()
    advisor_form.lecturer_id.choices = [(u.id, u.username) for u in lecturers]
    return render_template('admin/users.html', users=users, form=form, advisor_form=advisor_form, search_query=search_query)


@admin_bp.route('/students', methods=['GET', 'POST'])
@login_required
@admin_required
def students():
    if request.method == 'POST':
        flash('Admins can view students but cannot create or manage them.', 'warning')
        return redirect(url_for('admin.students'))

    level_filter = request.args.get('level', '').strip()
    search_query = request.args.get('search', '').strip()
    advisor_id = request.args.get('advisor', '').strip()
    show_all = request.args.get('show_all') == '1'
    can_view_list = False

    query = Student.query

    advisors = User.query.filter_by(role='lecturer', is_advisor=True).order_by(User.username).all()
    if not show_all:
        advisor_levels = [a.advisor_level for a in advisors if a.advisor_level]
        if advisor_levels:
            query = query.filter(Student.level.in_(advisor_levels))
        else:
            query = query.filter(Student.id == -1)

    if level_filter:
        query = query.filter_by(level=level_filter)

    if search_query:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{search_query}%"),
                Student.matric_no.ilike(f"%{search_query}%"),
                Student.user.has(User.email.ilike(f"%{search_query}%"))
            )
        )

    advisor_map = {}
    for adv in advisors:
        if adv.advisor_level:
            advisor_map.setdefault(adv.advisor_level, []).append(adv.username)

    if advisor_id:
        try:
            advisor = User.query.filter_by(id=int(advisor_id), is_advisor=True).first()
            if advisor and advisor.advisor_level:
                completed = AdvisorStudentListRequest.query.filter_by(
                    advisor_id=advisor.id,
                    admin_id=current_user.id,
                    status='completed'
                ).first()
                if completed:
                    can_view_list = True
                    query = query.filter_by(level=advisor.advisor_level)
                else:
                    query = query.filter(Student.id == -1)
        except Exception:
            pass

    completed_requests = AdvisorStudentListRequest.query.filter_by(status='completed').order_by(AdvisorStudentListRequest.responded_at.desc()).all()
    has_any_completed = len(completed_requests) > 0

    if not has_any_completed and not show_all:
        students = []
    else:
        students = query.order_by(Student.level, Student.name).all()

    levels = [l[0] for l in db.session.query(Student.level).distinct().order_by(Student.level).all()]

    list_request_form = AdvisorListRequestForm()
    list_request_form.advisor_id.choices = [(u.id, u.username) for u in advisors]
    requests = AdvisorStudentListRequest.query.order_by(AdvisorStudentListRequest.requested_at.desc()).all()

    return render_template(
        'admin/students.html',
        students=students,
        level_filter=level_filter,
        levels=levels,
        search_query=search_query,
        advisor_map=advisor_map,
        advisors=advisors,
        advisor_filter=advisor_id,
        show_all=show_all,
        list_request_form=list_request_form,
        requests=requests,
        completed_requests=completed_requests,
        can_view_list=can_view_list,
        has_any_completed=has_any_completed
    )


@admin_bp.route('/courses', methods=['GET', 'POST'])
@login_required
@admin_required
def courses():
    form = CourseForm()
    lecturers = [(u.id, u.username) for u in User.query.filter_by(role='lecturer').all()]
    form.lecturer_id.choices = lecturers

    if form.validate_on_submit():
        try:
            create_course(form.code.data, form.title.data, form.unit.data, form.semester.data, form.level.data, form.lecturer_id.data)
            flash('Course created', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            flash(str(e), 'danger')

    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses, form=form)


@admin_bp.route('/results', methods=['GET', 'POST'])
@login_required
@admin_required
def results():
    flash('Use Result Approval Requests to review results submitted by advisors.', 'info')
    return redirect(url_for('admin.result_requests'))


@admin_bp.route('/result-requests')
@login_required
@admin_required
def result_requests():
    session_name = request.args.get('session', '').strip()
    level_filter = request.args.get('level', '').strip()
    department_filter = request.args.get('department', '').strip()
    status = request.args.get('status', 'advisor_submitted').strip()

    query = AdvisorResultSubmission.query
    if status:
        query = query.filter_by(status=status)

    if session_name:
        session = AcademicSession.query.filter_by(name=session_name).first()
        if session:
            query = query.filter_by(session_id=session.id)
    if level_filter:
        query = query.filter_by(level=level_filter)
    if department_filter:
        query = query.filter_by(department=department_filter)

    requests = query.order_by(AdvisorResultSubmission.submitted_at.desc()).all()
    sessions = AcademicSession.query.all()
    levels = [l[0] for l in db.session.query(Student.level).distinct().order_by(Student.level).all()]
    departments = [d[0] for d in db.session.query(Student.department).distinct().order_by(Student.department).all()]
    return render_template(
        'admin/result_requests.html',
        requests=requests,
        sessions=sessions,
        levels=levels,
        departments=departments,
        session_name=session_name,
        level_filter=level_filter,
        department_filter=department_filter,
        status=status
    )


@admin_bp.route('/result-requests/<int:request_id>')
@login_required
@admin_required
def view_result_request(request_id):
    req = AdvisorResultSubmission.query.get_or_404(request_id)
    students = Student.query.filter_by(level=req.level, department=req.department).order_by(Student.name).all()

    student_rows = []
    for s in students:
        results = Result.query.filter_by(
            student_id=s.id,
            session_id=req.session_id,
            semester=req.semester
        ).all()
        pending = [r for r in results if r.approval_status == 'pending']
        student_rows.append({
            'student': s,
            'total_results': len(results),
            'pending_results': len(pending)
        })

    return render_template('admin/result_request_students.html', req=req, student_rows=student_rows)


@admin_bp.route('/result-requests/<int:request_id>/student/<int:student_id>')
@login_required
@admin_required
def view_result_request_student(request_id, student_id):
    req = AdvisorResultSubmission.query.get_or_404(request_id)
    student = Student.query.get_or_404(student_id)
    if student.level != req.level or student.department != req.department:
        flash('Student not in this submission.', 'warning')
        return redirect(url_for('admin.view_result_request', request_id=req.id))

    results = Result.query.filter_by(
        student_id=student.id,
        session_id=req.session_id,
        semester=req.semester
    ).all()
    return render_template('admin/result_request_student_detail.html', req=req, student=student, results=results)


@admin_bp.route('/result-requests/<int:request_id>/complete', methods=['POST'])
@login_required
@admin_required
def complete_result_request(request_id):
    req = AdvisorResultSubmission.query.get_or_404(request_id)
    pending = Result.query.join(Student).filter(
        Student.level == req.level,
        Student.department == req.department,
        Result.session_id == req.session_id,
        Result.semester == req.semester,
        Result.approval_status == 'pending'
    ).count()
    if pending > 0:
        flash('There are still pending results. Approve or reject them first.', 'warning')
        return redirect(url_for('admin.view_result_request', request_id=req.id))

    req.status = 'admin_approved'
    req.admin_id = current_user.id
    req.admin_approved_at = db.func.now()
    db.session.commit()
    flash('Submission marked as approved.', 'success')
    return redirect(url_for('admin.result_requests', status='admin_approved'))


@admin_bp.route('/result-requests/<int:request_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_result_request(request_id):
    req = AdvisorResultSubmission.query.get_or_404(request_id)
    note = (request.form.get('note') or '').strip() or 'Sent back for correction'
    req.status = 'rejected'
    req.note = note
    req.admin_id = current_user.id
    req.admin_approved_at = db.func.now()
    if req.advisor_id:
        db.session.add(Notification(
            user_id=req.advisor_id,
            message=f"Result submission sent back ({req.level} {req.department}, {req.session.name} {req.semester}). Reason: {note}",
            link=url_for('lecturer.advisor_results', session=req.session.name, semester=req.semester, department=req.department)
        ))
    db.session.commit()
    flash('Submission sent back to advisor.', 'warning')
    return redirect(url_for('admin.result_requests', status='advisor_submitted'))


@admin_bp.route('/sessions', methods=['GET', 'POST'])
@login_required
@admin_required
def sessions():
    form = AcademicSessionForm()
    if form.validate_on_submit():
        try:
            create_session(form.name.data)
            flash('Session added', 'success')
            return redirect(url_for('admin.sessions'))
        except Exception as e:
            flash(str(e), 'danger')

    sessions = AcademicSession.query.all()
    return render_template('admin/sessions.html', sessions=sessions, form=form)


@admin_bp.route('/user/<int:id>/reset_password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(id):
    user = User.query.get_or_404(id)
    new_password = User.generate_random_password() if hasattr(User, 'generate_random_password') else 'ChangeMe123!'
    user.set_password(new_password)
    db.session.commit()
    flash(f"Password for {user.username} has been reset to '{new_password}'. Please share this securely.", 'success')
    return redirect(url_for('admin.user_list'))


@admin_bp.route('/session/<int:id>/activate')
@login_required
@admin_required
def activate_session_route(id):
    try:
        s = activate_session(id)
        flash(f'Session {s.name} activated', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.sessions'))


@admin_bp.route('/results/<int:result_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_result(result_id):
    res = Result.query.get_or_404(result_id)
    res.is_approved = True
    res.approval_status = 'approved'
    res.rejection_reason = None
    res.approved_by = current_user.id
    res.approved_at = db.func.now()
    db.session.add(ResultApprovalHistory(
        result_id=res.id,
        action='approved',
        note='Approved by admin',
        acted_by=current_user.id
    ))
    if res.course and res.course.lecturer_id:
        db.session.add(Notification(
            user_id=res.course.lecturer_id,
            message=f"Result approved for {res.course.code} ({res.student.matric_no})",
            link=url_for('lecturer.course_results', course_id=res.course.id)
        ))
    db.session.commit()
    flash('Result approved.', 'success')
    return redirect(request.referrer or url_for('admin.result_requests'))


@admin_bp.route('/results/<int:result_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_result(result_id):
    res = Result.query.get_or_404(result_id)
    note = (request.form.get('note') or '').strip() or 'Rejected by admin'
    res.is_approved = False
    res.approval_status = 'rejected'
    res.rejection_reason = note
    res.approved_by = current_user.id
    res.approved_at = db.func.now()
    db.session.add(ResultApprovalHistory(
        result_id=res.id,
        action='rejected',
        note=note,
        acted_by=current_user.id
    ))
    if res.course and res.course.lecturer_id:
        db.session.add(Notification(
            user_id=res.course.lecturer_id,
            message=f"Result rejected for {res.course.code} ({res.student.matric_no}). Reason: {note}",
            link=url_for('lecturer.course_results', course_id=res.course.id)
        ))
    db.session.commit()
    flash('Result rejected and sent back to lecturer.', 'warning')
    return redirect(request.referrer or url_for('admin.result_requests'))


@admin_bp.route('/advisors/assign', methods=['POST'])
@login_required
@admin_required
def assign_advisor():
    form = AdvisorAssignForm()
    lecturers = User.query.filter_by(role='lecturer').order_by(User.username).all()
    form.lecturer_id.choices = [(u.id, u.username) for u in lecturers]

    if form.validate_on_submit():
        lecturer = User.query.get(form.lecturer_id.data)
        if not lecturer or lecturer.role != 'lecturer':
            flash('Invalid lecturer selected', 'danger')
            return redirect(url_for('admin.user_list'))

        level = (form.level.data or '').strip()
        if level:
            lecturer.is_advisor = True
            lecturer.advisor_level = level
            flash(f'{lecturer.username} assigned as advisor for level {level}', 'success')
        else:
            lecturer.is_advisor = False
            lecturer.advisor_level = None
            flash(f'{lecturer.username} advisor status cleared', 'success')

        db.session.commit()
        return redirect(url_for('admin.user_list'))

    for error in form.errors.values():
        if error:
            flash(error[0], 'danger')
            break
    return redirect(url_for('admin.user_list'))


@admin_bp.route('/advisors/requests', methods=['POST'])
@login_required
@admin_required
def request_advisor_student_list():
    form = AdvisorListRequestForm()
    advisors = User.query.filter_by(role='lecturer', is_advisor=True).order_by(User.username).all()
    form.advisor_id.choices = [(u.id, u.username) for u in advisors]

    if form.validate_on_submit():
        req = AdvisorStudentListRequest(
            admin_id=current_user.id,
            advisor_id=form.advisor_id.data,
            status='pending',
            note=(form.note.data or '').strip() or None
        )
        db.session.add(req)
        db.session.commit()
        flash('Request sent to advisor.', 'success')
        return redirect(url_for('admin.students'))

    flash('Unable to submit request.', 'danger')
    return redirect(url_for('admin.students'))


@admin_bp.route('/advisors/requests/<int:request_id>/students.csv')
@login_required
@admin_required
def export_advisor_students_csv(request_id):
    req = AdvisorStudentListRequest.query.get_or_404(request_id)
    advisor = User.query.filter_by(id=req.advisor_id, role='lecturer', is_advisor=True).first()
    if not advisor or not advisor.advisor_level:
        flash('Advisor has no assigned level.', 'warning')
        return redirect(url_for('admin.students'))

    if req.csv_path:
        try:
            return send_file(req.csv_path, as_attachment=True)
        except Exception:
            pass

    students = Student.query.filter_by(level=advisor.advisor_level).order_by(Student.name).all()
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
            advisor.username.replace(',', ' ')
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
    filepath = os.path.join(folder, f"advisor_{advisor.username}_request_{req.id}.csv")
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(csv_data)

    req.csv_path = filepath
    if req.status != 'completed':
        req.status = 'completed'
    db.session.commit()
    return send_file(filepath, as_attachment=True)
