from datetime import datetime
from ..extensions import db


class ResitRequest(db.Model):
    __tablename__ = 'resit_requests'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    target_semester = db.Column(db.String(6), nullable=True)
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    enrolled_session_id = db.Column(db.Integer, db.ForeignKey('academic_session.id'), nullable=True)

    student = db.relationship('Student', backref='resit_requests')
    course = db.relationship('Course', backref='resit_requests')
    reviewer = db.relationship('User', backref='reviewed_resit_requests')
    enrolled_session = db.relationship('AcademicSession', backref='resit_enrollments')
